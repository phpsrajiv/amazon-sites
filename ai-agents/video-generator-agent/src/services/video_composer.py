"""
Video Composer Service
========================
Uses MoviePy v2.x (FFmpeg wrapper) to composite video clips, audio narration,
and text overlays into final segment clips, then concatenate all segments
into the final video.

Output: 1080p, 30fps, H.264 video, AAC audio.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

logger = logging.getLogger(__name__)


class VideoComposer:
    """Compose video segments with audio and text overlays."""

    def __init__(self) -> None:
        self.fps = 30
        self.resolution = (1920, 1080)  # 1080p
        self.font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        self.font_size = 48
        self.text_color = "white"
        self.text_bg_opacity = 0.6

    def compose_segment(
        self,
        video_paths: "str | List[str]",
        audio_path: str,
        on_screen_text: str = "",
        target_duration: Optional[int] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Compose a single segment: video(s) + audio + text overlay.

        Args:
            video_paths: Path to a single B-roll clip OR a list of multiple
                         unique clips to concatenate (no looping/repetition).
            audio_path: Path to the narration audio (from TTS).
            on_screen_text: Text to overlay on the video.
            target_duration: Target duration in seconds. If None, uses audio length.
            output_path: Where to save the composed segment.

        Returns:
            Path to the composed segment MP4.
        """
        # Normalise to list
        if isinstance(video_paths, str):
            video_paths = [video_paths]

        if output_path is None:
            output_path = video_paths[0].replace(".mp4", "_composed.mp4")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Composing segment: %d video clip(s), audio=%s",
            len(video_paths), audio_path,
        )

        # Load audio to determine final duration
        audio = AudioFileClip(audio_path)
        final_duration = target_duration or audio.duration

        # Load and concatenate all video clips
        clips = [VideoFileClip(p) for p in video_paths]
        if len(clips) > 1:
            video = concatenate_videoclips(clips, method="compose")
        else:
            video = clips[0]

        # Trim or extend to match final duration
        if video.duration < final_duration:
            # Only loop as a last resort (e.g. if clips still don't fill)
            from moviepy import vfx
            num_loops = int(final_duration / video.duration) + 1
            video = video.with_effects([vfx.Loop(n=num_loops)])
        video = video.subclipped(0, final_duration)

        # Resize to target resolution if needed
        if video.size != list(self.resolution):
            video = video.resized(self.resolution)

        # Build layers
        layers = [video]

        # Add text overlay if provided
        if on_screen_text and on_screen_text.strip():
            text_clip = self._create_text_overlay(
                on_screen_text, video.w, final_duration
            )
            layers.append(text_clip)

        # Composite all layers
        composite = CompositeVideoClip(layers, size=self.resolution)

        # Set audio (narration replaces original video audio)
        audio_trimmed = audio.subclipped(0, min(audio.duration, final_duration))
        composite = composite.with_audio(audio_trimmed)

        # Write output
        composite.write_videofile(
            output_path,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,  # Suppress moviepy progress bars
        )

        # Clean up
        for c in clips:
            c.close()
        video.close()
        audio.close()
        composite.close()

        logger.info("Segment composed: %s (%.1fs)", output_path, final_duration)
        return output_path

    def _create_text_overlay(
        self, text: str, video_width: int, duration: float
    ) -> CompositeVideoClip:
        """Create a text overlay with semi-transparent background bar."""

        # Create the text clip
        txt = (
            TextClip(
                text=text,
                font_size=self.font_size,
                color=self.text_color,
                font=self.font,
                method="caption",
                size=(int(video_width * 0.9), None),
                text_align="center",
            )
            .with_duration(duration)
        )

        # Create semi-transparent background bar
        txt_height = txt.h + 20  # Padding
        bg = (
            ColorClip(
                size=(video_width, txt_height),
                color=(0, 0, 0),
            )
            .with_opacity(self.text_bg_opacity)
            .with_duration(duration)
        )

        # Position background at bottom
        bg = bg.with_position(("center", self.resolution[1] - txt_height))

        # Position text centered on the background bar
        txt = txt.with_position(("center", self.resolution[1] - txt_height + 10))

        return CompositeVideoClip(
            [bg, txt],
            size=self.resolution,
        ).with_duration(duration)

    def concatenate_segments(
        self,
        segment_paths: List[str],
        output_path: str,
    ) -> str:
        """
        Concatenate all composed segments into the final video.

        Args:
            segment_paths: Ordered list of segment MP4 file paths.
            output_path: Path for the final output video.

        Returns:
            Path to the final concatenated video.
        """
        logger.info("Concatenating %d segments into final video...", len(segment_paths))

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        clips = [VideoFileClip(p) for p in segment_paths]

        final = concatenate_videoclips(clips, method="compose")

        final.write_videofile(
            output_path,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,
        )

        # Clean up
        for clip in clips:
            clip.close()
        final.close()

        # Get file size
        file_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB

        logger.info(
            "Final video created: %s (%.1f MB)", output_path, file_size
        )
        return output_path
