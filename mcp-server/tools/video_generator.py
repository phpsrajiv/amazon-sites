"""
Video Generator Agent tools — wraps http://localhost:8004

Video generation is async: submit a job, poll for status, retrieve result.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from utils import client


def register(mcp: FastMCP) -> None:

    @mcp.tool()
    def video_generator_health() -> dict:
        """
        Check whether the Video Generator Agent is running and its integrations
        (Google Veo, ElevenLabs, Google TTS) are configured.
        """
        return client.get("video_generator", "/health")

    @mcp.tool()
    def video_generate(youtube_script_json: str) -> dict:
        """
        Start an async video generation job from a YouTube script.

        Uses Google Veo 3.1 for B-roll, ElevenLabs/Google TTS for narration,
        and MoviePy for final composition. Returns a job_id immediately —
        the actual generation runs in the background.

        After calling this, poll video_job_status(job_id) until status is
        "completed", then call video_job_result(job_id) for metadata.

        Args:
            youtube_script_json: JSON string of a YouTubeScriptResponse
                                 (output of video_youtube_script or
                                  video_script_full_pipeline)
        """
        script = json.loads(youtube_script_json)
        return client.post("video_generator", "/api/generate/video", {
            "youtube_script": script,
        })

    @mcp.tool()
    def video_job_status(job_id: str) -> dict:
        """
        Check the progress of a video generation job.

        Returns status ("queued" | "processing" | "completed" | "failed"),
        progress_percent, current_step, and error_message if failed.

        Args:
            job_id: Job ID returned by video_generate
        """
        return client.get("video_generator", f"/api/generate/status/{job_id}")

    @mcp.tool()
    def video_job_result(job_id: str) -> dict:
        """
        Get the final metadata of a completed video generation job.

        Returns video_path, duration_seconds, file_size_mb, segments_count,
        and other composition details. Only call this once
        video_job_status returns status="completed".

        Args:
            job_id: Job ID returned by video_generate
        """
        return client.get("video_generator", f"/api/generate/result/{job_id}")

    @mcp.tool()
    def video_download_url(job_id: str) -> dict:
        """
        Return the download URL for a completed video file (MP4).

        The video is served directly from the Video Generator Agent at
        /api/generate/download/{job_id}. Only valid after the job completes.

        Args:
            job_id: Job ID returned by video_generate
        """
        base = client.agent_url("video_generator")
        return {
            "download_url": f"{base}/api/generate/download/{job_id}",
            "format": "mp4",
            "job_id": job_id,
        }
