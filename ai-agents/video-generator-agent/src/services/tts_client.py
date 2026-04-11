"""
Text-to-Speech Client Abstraction
====================================
Supports both ElevenLabs and Google Cloud TTS.
Factory function returns the correct implementation based on provider name.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSClient(ABC):
    """Base class for text-to-speech providers."""

    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> str:
        """
        Convert text to speech and save as audio file.

        Args:
            text: The text to convert to speech.
            output_path: Path to save the audio file (MP3).

        Returns:
            Path to the saved audio file.
        """
        ...


class ElevenLabsTTS(TTSClient):
    """ElevenLabs TTS — natural, expressive voices for video narration."""

    def __init__(self, voice_id: str | None = None) -> None:
        from elevenlabs.client import ElevenLabs

        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is required.")

        self.client = ElevenLabs(api_key=api_key)
        # Default to a professional male voice; can be overridden
        self.voice_id = voice_id or os.getenv(
            "ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb"
        )
        self.model_id = os.getenv(
            "ELEVENLABS_MODEL", "eleven_multilingual_v2"
        )

    def synthesize(self, text: str, output_path: str) -> str:
        logger.info(
            "ElevenLabs TTS: generating audio (voice=%s, %d chars)",
            self.voice_id, len(text),
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Generate audio using streaming for efficiency
        audio_stream = self.client.text_to_speech.convert(
            text=text,
            voice_id=self.voice_id,
            model_id=self.model_id,
            output_format="mp3_44100_128",
        )

        # Collect all audio bytes
        audio_bytes = b""
        for chunk in audio_stream:
            if isinstance(chunk, bytes):
                audio_bytes += chunk

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        logger.info("ElevenLabs audio saved to: %s", output_path)
        return output_path


class GoogleTTS(TTSClient):
    """Google Cloud Text-to-Speech — broad language support, generous free tier."""

    def __init__(self) -> None:
        from google.cloud import texttospeech

        self.client = texttospeech.TextToSpeechClient()
        self.voice_name = os.getenv("GOOGLE_TTS_VOICE", "en-US-Neural2-C")
        self.language_code = os.getenv("GOOGLE_TTS_LANGUAGE", "en-US")
        self._texttospeech = texttospeech

    def synthesize(self, text: str, output_path: str) -> str:
        logger.info(
            "Google TTS: generating audio (voice=%s, %d chars)",
            self.voice_name, len(text),
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        synthesis_input = self._texttospeech.SynthesisInput(text=text)

        voice = self._texttospeech.VoiceSelectionParams(
            language_code=self.language_code,
            name=self.voice_name,
        )

        audio_config = self._texttospeech.AudioConfig(
            audio_encoding=self._texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        logger.info("Google TTS audio saved to: %s", output_path)
        return output_path


def get_tts_client(
    provider: str = "elevenlabs",
    voice_id: str | None = None,
) -> TTSClient:
    """
    Factory function — returns the correct TTS client.

    Args:
        provider: "elevenlabs" or "google".
        voice_id: Optional voice ID (ElevenLabs only).

    Returns:
        TTSClient instance.
    """
    if provider == "elevenlabs":
        return ElevenLabsTTS(voice_id=voice_id)
    elif provider == "google":
        return GoogleTTS()
    else:
        raise ValueError(
            f"Unknown TTS provider: '{provider}'. Use 'elevenlabs' or 'google'."
        )
