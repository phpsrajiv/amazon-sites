"""
Google Veo 3.1 API Client
===========================
Generates video clips from text prompts using the Google GenAI SDK.
Uses the Veo 3.1 Fast model by default ($0.15/second).

Video generation is async — we submit a job, poll until done, then
download the resulting MP4 to a local temp file.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path

import requests
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Pricing per second by model tier
VEO_PRICING = {
    "veo-3.1-generate-preview": 0.15,       # Fast
    "veo-3.1-fast-generate-preview": 0.15,   # Fast alias
    "veo-3.0-generate-preview": 0.75,        # Full quality
}


class VeoClient:
    """Generate video clips using Google Veo 3.1 API."""

    def __init__(self) -> None:
        api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_GENAI_API_KEY environment variable is required.")

        self.client = genai.Client(api_key=api_key)
        self.default_model = os.getenv(
            "VEO_MODEL", "veo-3.1-generate-preview"
        )

    def generate_clip(
        self,
        prompt: str,
        duration_seconds: int = 8,
        aspect_ratio: str = "16:9",
        model: str | None = None,
        output_path: str | None = None,
        poll_interval: int = 20,
        max_wait: int = 600,
    ) -> str:
        """
        Generate a video clip from a text prompt.

        Args:
            prompt: Descriptive prompt for the video clip (e.g. B-roll suggestion).
            duration_seconds: Desired clip length (8-60 seconds).
            aspect_ratio: "16:9", "9:16", or "1:1".
            model: Veo model name. Defaults to veo-3.1-generate-preview.
            output_path: Where to save the MP4 file. Auto-generated if None.
            poll_interval: Seconds between status polls.
            max_wait: Maximum seconds to wait before timeout.

        Returns:
            Path to the downloaded MP4 file.

        Raises:
            TimeoutError: If generation exceeds max_wait.
            RuntimeError: If generation fails.
        """
        model_name = model or self.default_model

        # Clamp duration to Veo 3.1 limits (4-8 seconds per clip)
        duration_seconds = max(4, min(duration_seconds, 8))

        logger.info(
            "Generating video clip: model=%s, duration=%ds, prompt='%.80s...'",
            model_name, duration_seconds, prompt,
        )

        # Step 1: Submit generation request
        operation = self.client.models.generate_videos(
            model=model_name,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                duration_seconds=duration_seconds,
                number_of_videos=1,
            ),
        )

        # Step 2: Poll for completion
        elapsed = 0
        while not operation.done:
            if elapsed >= max_wait:
                raise TimeoutError(
                    f"Video generation timed out after {max_wait}s. "
                    f"Operation: {operation.name}"
                )
            logger.info(
                "Waiting for video generation... (%ds elapsed)", elapsed
            )
            time.sleep(poll_interval)
            elapsed += poll_interval
            operation = self.client.operations.get(operation)

        # Step 3: Download the generated video
        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError(
                f"Video generation completed but no videos returned. "
                f"Operation: {operation.name}"
            )

        video = operation.response.generated_videos[0]
        video_uri = video.video.uri

        logger.info("Video generated successfully: %s", video_uri)

        # Download video to local file
        if output_path is None:
            output_path = f"/tmp/veo_clip_{int(time.time())}.mp4"

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Try to get video bytes directly from the SDK response first
        if hasattr(video.video, "video_bytes") and video.video.video_bytes:
            with open(output_path, "wb") as f:
                f.write(video.video.video_bytes)
        else:
            # Download from URI — append API key for authenticated endpoints
            api_key = os.getenv("GOOGLE_GENAI_API_KEY", "")
            download_url = video_uri

            # For generativelanguage.googleapis.com URLs, append API key
            if "googleapis.com" in download_url:
                separator = "&" if "?" in download_url else "?"
                download_url = f"{download_url}{separator}key={api_key}"
            elif download_url.startswith("gs://"):
                bucket_path = download_url.replace("gs://", "")
                download_url = f"https://storage.googleapis.com/{bucket_path}"

            resp = requests.get(download_url, timeout=120)
            resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(resp.content)

        logger.info("Video clip saved to: %s", output_path)
        return output_path

    def estimate_cost(self, duration_seconds: int, model: str | None = None) -> float:
        """Estimate cost in USD for a video clip."""
        model_name = model or self.default_model
        rate = VEO_PRICING.get(model_name, 0.15)
        return duration_seconds * rate
