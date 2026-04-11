"""
Video Generator Agent API for SellerBuddy
==========================================
Takes YouTube script output (from Video Script Agent) and produces actual
video files using:
  - Google Veo 3.1 API for B-roll video generation
  - ElevenLabs / Google TTS for narration audio
  - MoviePy for composition (video + audio + text overlays)

Generation runs asynchronously — submit a job, poll for status, download when done.
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from src.models.video_generation import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoGenerationStatus,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SellerBuddy — Video Generator Agent",
    description=(
        "Takes YouTube script output and produces actual video files using "
        "Google Veo 3.1 for B-roll, ElevenLabs/Google TTS for narration, "
        "and MoviePy for composition."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Lazy-loaded singleton
# ---------------------------------------------------------------------------

_generator = None


def get_generator():
    global _generator
    if _generator is None:
        from src.agents.video_generator import VideoGenerator
        _generator = VideoGenerator()
    return _generator


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/api/generate/video")
async def generate_video(request: VideoGenerationRequest) -> dict:
    """
    Start a video generation job.

    Accepts a YouTubeScriptResponse (from Video Script Agent) and begins
    generating video in the background. Returns a job_id immediately.

    Poll /api/generate/status/{job_id} to check progress.
    Download from /api/generate/download/{job_id} when completed.
    """
    try:
        if not request.youtube_script or not request.youtube_script.segments:
            raise HTTPException(
                status_code=400,
                detail="youtube_script with at least one segment is required.",
            )

        generator = get_generator()
        job_id = generator.submit_job(request)

        return {
            "job_id": job_id,
            "status": "queued",
            "total_segments": len(request.youtube_script.segments),
            "estimated_duration_minutes": len(request.youtube_script.segments) * 3,
            "message": (
                f"Video generation started. Poll /api/generate/status/{job_id} "
                f"to check progress."
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error starting video generation")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/generate/status/{job_id}", response_model=VideoGenerationStatus)
async def generation_status(job_id: str):
    """Check the progress of a video generation job."""
    from src.agents.video_generator import get_job_status

    status = get_job_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    return status


@app.get("/api/generate/result/{job_id}", response_model=VideoGenerationResponse)
async def generation_result(job_id: str):
    """Get the final result (metadata) of a completed video generation job."""
    from src.agents.video_generator import get_job_response

    response = get_job_response(job_id)
    if not response:
        # Check if job exists but isn't complete
        from src.agents.video_generator import get_job_status
        status = get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
        if status.status == "failed":
            raise HTTPException(
                status_code=500,
                detail=f"Job failed: {status.error_message}",
            )
        raise HTTPException(
            status_code=202,
            detail=f"Job is still in progress (status: {status.status}, "
                   f"progress: {status.progress_percent:.0f}%).",
        )

    return response


@app.get("/api/generate/download/{job_id}")
async def download_video(job_id: str):
    """Download the completed video file."""
    from src.agents.video_generator import get_job_response

    response = get_job_response(job_id)
    if not response:
        from src.agents.video_generator import get_job_status
        status = get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
        raise HTTPException(
            status_code=202,
            detail=f"Job not yet completed (status: {status.status}).",
        )

    video_path = Path(response.video_path)
    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video file not found on disk. It may have been cleaned up.",
        )

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=f"{job_id}.mp4",
    )


@app.get("/health")
async def health():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "video-generator-agent",
        "google_genai_configured": bool(os.getenv("GOOGLE_GENAI_API_KEY")),
        "elevenlabs_configured": bool(os.getenv("ELEVENLABS_API_KEY")),
        "google_tts_configured": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
    }
