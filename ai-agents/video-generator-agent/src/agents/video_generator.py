"""
Video Generator — Core Orchestrator
======================================
Takes a YouTubeScriptResponse and produces a complete video:

For each ScriptSegment:
  1. Generate MULTIPLE unique B-roll clips → Veo 3.1 API (8s each)
     Each clip uses a varied prompt to avoid visual repetition.
  2. Generate narration audio  → ElevenLabs or Google TTS
  3. Compose segment          → MoviePy (concatenated clips + audio + text)

Then concatenate all segments into the final MP4.

Runs in a background thread because Veo generation takes 2-5 minutes
per clip. Progress is tracked via an in-memory job status dict.
"""

from __future__ import annotations

import logging
import os
import shutil
import time
import uuid
from pathlib import Path
from threading import Thread
from typing import Dict

from src.models.youtube_script import YouTubeScriptResponse
from src.models.video_generation import (
    SegmentStatus,
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoGenerationStatus,
)
from src.services.veo_client import VeoClient
from src.services.tts_client import get_tts_client
from src.services.video_composer import VideoComposer

logger = logging.getLogger(__name__)

# In-memory job tracking
_jobs: Dict[str, VideoGenerationStatus] = {}

OUTPUT_DIR = os.getenv("VIDEO_OUTPUT_DIR", "/app/output")


class VideoGenerator:
    """Orchestrate end-to-end video generation from a script."""

    def __init__(self) -> None:
        self.veo = VeoClient()
        self.composer = VideoComposer()

    def submit_job(self, request: VideoGenerationRequest) -> str:
        """
        Submit a video generation job. Returns job_id immediately.
        Generation runs in a background thread.
        """
        job_id = str(uuid.uuid4())[:12]
        script = request.youtube_script

        # Initialize job status
        status = VideoGenerationStatus(
            job_id=job_id,
            status="queued",
            progress_percent=0.0,
            current_segment=0,
            total_segments=len(script.segments),
            segments=[
                SegmentStatus(
                    segment_index=i,
                    section_title=seg.section_title,
                )
                for i, seg in enumerate(script.segments)
            ],
        )
        _jobs[job_id] = status

        # Launch generation in background thread
        thread = Thread(
            target=self._run_generation,
            args=(job_id, request),
            daemon=True,
        )
        thread.start()

        logger.info("Job %s submitted (%d segments)", job_id, len(script.segments))
        return job_id

    def get_status(self, job_id: str) -> VideoGenerationStatus | None:
        """Get current status of a generation job."""
        return _jobs.get(job_id)

    def _run_generation(self, job_id: str, request: VideoGenerationRequest) -> None:
        """Background thread: generate video for all segments."""
        status = _jobs[job_id]
        script = request.youtube_script
        work_dir = f"/tmp/video-gen/{job_id}"
        Path(work_dir).mkdir(parents=True, exist_ok=True)

        # Initialize TTS client
        tts = get_tts_client(
            provider=request.tts_provider,
            voice_id=request.voice_id,
        )

        composed_segments: list[str] = []
        total_cost = 0.0

        try:
            for i, segment in enumerate(script.segments):
                status.current_segment = i + 1
                seg_status = status.segments[i]

                segment_dir = f"{work_dir}/segment_{i:03d}"
                Path(segment_dir).mkdir(parents=True, exist_ok=True)

                # --- Step 1: Generate MULTIPLE B-roll clips with Veo ---
                status.status = "generating_video"
                status.progress_percent = (i / len(script.segments)) * 100

                # Calculate how many unique 8-second clips we need.
                # Veo 3.1 max clip length is 8 seconds.
                clip_duration = 8
                num_clips = max(1, -(-segment.duration_seconds // clip_duration))  # ceil division

                # Build varied prompts so each clip looks different
                clip_prompts = self._build_varied_prompts(
                    b_roll_suggestion=segment.b_roll_suggestion,
                    section_title=segment.section_title,
                    video_title=script.title,
                    num_clips=num_clips,
                )

                video_paths: list[str] = []
                try:
                    for ci, prompt in enumerate(clip_prompts):
                        logger.info(
                            "Generating clip %d/%d for segment %d",
                            ci + 1, num_clips, i,
                        )
                        clip_path = self.veo.generate_clip(
                            prompt=prompt,
                            duration_seconds=clip_duration,
                            aspect_ratio=request.aspect_ratio,
                            model=request.veo_model,
                            output_path=f"{segment_dir}/broll_{ci:02d}.mp4",
                        )
                        video_paths.append(clip_path)
                        total_cost += self.veo.estimate_cost(
                            clip_duration, request.veo_model
                        )

                    seg_status.video_generated = True

                except Exception as e:
                    logger.error("Veo failed for segment %d, clip %d: %s", i, len(video_paths), e)
                    seg_status.error = f"Video generation failed: {e}"

                    if not video_paths:
                        # No clips at all — use a black placeholder
                        video_paths = [
                            self._create_placeholder_video(
                                segment_dir, segment.duration_seconds
                            )
                        ]
                    # Otherwise we continue with whatever clips we got
                    seg_status.video_generated = True

                # --- Step 2: Generate narration audio with TTS ---
                status.status = "generating_audio"

                try:
                    audio_path = tts.synthesize(
                        text=segment.narration,
                        output_path=f"{segment_dir}/narration.mp3",
                    )
                    seg_status.audio_generated = True

                except Exception as e:
                    logger.error("TTS failed for segment %d: %s", i, e)
                    seg_status.error = f"Audio generation failed: {e}"
                    # Create silent audio placeholder
                    audio_path = self._create_silent_audio(
                        segment_dir, segment.duration_seconds
                    )
                    seg_status.audio_generated = True

                # --- Step 3: Compose segment (video + audio + text) ---
                status.status = "composing"

                try:
                    composed_path = self.composer.compose_segment(
                        video_paths=video_paths,
                        audio_path=audio_path,
                        on_screen_text=segment.on_screen_text,
                        target_duration=segment.duration_seconds,
                        output_path=f"{segment_dir}/composed.mp4",
                    )
                    seg_status.composed = True
                    composed_segments.append(composed_path)

                except Exception as e:
                    logger.error("Composition failed for segment %d: %s", i, e)
                    seg_status.error = f"Composition failed: {e}"
                    status.status = "failed"
                    status.error_message = (
                        f"Segment {i} ({segment.section_title}) composition failed: {e}"
                    )
                    return

            # --- Step 4: Concatenate all segments ---
            status.status = "composing"
            status.progress_percent = 95.0

            # Ensure output directory exists
            Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
            final_path = f"{OUTPUT_DIR}/{job_id}.mp4"

            self.composer.concatenate_segments(
                segment_paths=composed_segments,
                output_path=final_path,
            )

            # Calculate final stats
            file_size_mb = Path(final_path).stat().st_size / (1024 * 1024)

            # Store response data in status for retrieval
            status.status = "completed"
            status.progress_percent = 100.0
            status._response = VideoGenerationResponse(
                job_id=job_id,
                video_path=final_path,
                duration_seconds=script.total_duration_seconds,
                file_size_mb=round(file_size_mb, 2),
                segments_generated=len(composed_segments),
                cost_estimate=round(total_cost, 2),
            )

            logger.info(
                "Job %s completed: %s (%.1f MB, $%.2f estimated cost)",
                job_id, final_path, file_size_mb, total_cost,
            )

        except Exception as e:
            logger.exception("Job %s failed: %s", job_id, e)
            status.status = "failed"
            status.error_message = str(e)

        finally:
            # Clean up temp working directory
            try:
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception:
                pass

    def _build_varied_prompts(
        self,
        b_roll_suggestion: str,
        section_title: str,
        video_title: str,
        num_clips: int,
    ) -> list[str]:
        """
        Build a list of varied prompts for Veo so each 8-second clip
        looks visually distinct — no repetition.

        Strategy: vary camera angle, movement, and focus for each clip.
        """
        # Camera/visual variations to cycle through
        variations = [
            "Wide establishing shot, slow dolly forward",
            "Close-up detail shot, shallow depth of field, slow pan right",
            "Medium shot from a slight low angle, smooth tracking movement",
            "Top-down overhead perspective, slow zoom out",
            "Handheld cinematic feel, slight movement, bokeh background",
            "Slow-motion macro shot with dramatic lighting",
            "Side angle tracking shot, parallax movement",
            "Bird's-eye view slowly rotating",
        ]

        prompts: list[str] = []
        for ci in range(num_clips):
            variation = variations[ci % len(variations)]
            prompt = (
                f"Professional B-roll footage: {b_roll_suggestion}. "
                f"{variation}. "
                f"High quality, cinematic, 16:9 aspect ratio. "
                f"Context: {section_title} section of a YouTube video "
                f"about {video_title}. "
                f"Unique scene — do not repeat previous shots."
            )
            prompts.append(prompt)

        return prompts

    def _create_placeholder_video(self, segment_dir: str, duration: int) -> str:
        """Create a black placeholder video when Veo fails."""
        from moviepy import ColorClip

        path = f"{segment_dir}/broll.mp4"
        clip = ColorClip(
            size=(1920, 1080), color=(0, 0, 0), duration=duration
        )
        clip.write_videofile(path, fps=30, codec="libx264", logger=None)
        clip.close()
        return path

    def _create_silent_audio(self, segment_dir: str, duration: int) -> str:
        """Create a silent audio file when TTS fails."""
        import subprocess

        path = f"{segment_dir}/narration.mp3"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"anullsrc=r=44100:cl=stereo",
                "-t", str(duration),
                "-q:a", "9",
                path,
            ],
            capture_output=True,
            timeout=30,
        )
        return path


def get_job_status(job_id: str) -> VideoGenerationStatus | None:
    """Module-level accessor for job status."""
    return _jobs.get(job_id)


def get_job_response(job_id: str) -> VideoGenerationResponse | None:
    """Get the final response for a completed job."""
    status = _jobs.get(job_id)
    if status and status.status == "completed" and hasattr(status, "_response"):
        return status._response
    return None
