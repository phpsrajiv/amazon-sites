"""Request / response / status models for the Video Generator Agent."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from src.models.youtube_script import YouTubeScriptResponse


class VideoGenerationRequest(BaseModel):
    youtube_script: YouTubeScriptResponse

    # TTS provider: "google" (default, free tier: 4M chars/month) or "elevenlabs".
    # To switch to ElevenLabs for more natural/expressive voices:
    #   1. Set tts_provider to "elevenlabs" in the request body
    #   2. Set ELEVENLABS_API_KEY in your .env / docker-compose environment
    #   3. Optionally set voice_id below (browse voices at https://elevenlabs.io/voice-library)
    tts_provider: str = "google"

    veo_model: str = "veo-3.1-generate-preview"  # Veo 3.1 Fast (default)

    # ElevenLabs voice ID — only used when tts_provider is "elevenlabs".
    # Default: "JBFqnCBsd6RMkjVDRZzb" (George — professional male narrator).
    # Find more voices at: https://elevenlabs.io/voice-library
    voice_id: Optional[str] = None

    aspect_ratio: str = "16:9"                # "16:9", "9:16", "1:1"
    output_format: str = "mp4"


class SegmentStatus(BaseModel):
    segment_index: int
    section_title: str
    video_generated: bool = False
    audio_generated: bool = False
    composed: bool = False
    error: Optional[str] = None


class VideoGenerationStatus(BaseModel):
    job_id: str
    status: str                               # "queued", "generating_video", "generating_audio",
                                              # "composing", "completed", "failed"
    progress_percent: float = 0.0
    current_segment: int = 0
    total_segments: int = 0
    segments: List[SegmentStatus] = []
    error_message: Optional[str] = None


class VideoGenerationResponse(BaseModel):
    job_id: str
    video_path: str
    duration_seconds: int
    file_size_mb: float
    segments_generated: int
    cost_estimate: float                      # Estimated cost in USD
