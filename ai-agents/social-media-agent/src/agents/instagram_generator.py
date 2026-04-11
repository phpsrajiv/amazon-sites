import os
import json
import re
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.models.instagram import (
    InstagramRequest,
    InstagramResponse,
    ReelScript,
    ReelSegment,
    InstagramCaption,
)
from src.models.logging import DecisionType

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


class InstagramGenerator:

    def __init__(self, agent_logger=None):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=0.7,
        )
        self.agent_logger = agent_logger

    def generate(self, req: InstagramRequest) -> InstagramResponse:
        event_ctx = ""
        if req.event_context:
            event_ctx = f"\nEvent context: {req.event_context}. Make the Reel timely and relevant to this event."

        messages = [
            SystemMessage(content=(
                "You are an expert Instagram Reels creator for Amazon sellers and D2C brands in India. "
                f"Brand: {req.brand}.\n\n"
                "Generate an Instagram Reel script + caption.\n\n"
                "REEL SCRIPT rules:\n"
                "- Hook in first 3 seconds (must stop the scroll)\n"
                "- 3-5 body segments with timestamp, visual, voiceover, and text overlay\n"
                "- Strong CTA at the end\n"
                f"- Target duration: {req.reel_duration} seconds\n"
                "- Suggest music mood (upbeat/dramatic/chill/motivational)\n"
                "- Include text overlays for key points\n\n"
                "CAPTION rules:\n"
                "- Engaging text (100-200 words)\n"
                "- 20-30 relevant hashtags (mix of high and low volume)\n\n"
                f"Tone: {req.tone.value}\n"
                f"{event_ctx}\n\n"
                "Respond in JSON:\n"
                "{\n"
                '  "reel_script": {\n'
                '    "hook": "first 3 seconds text",\n'
                '    "segments": [{"timestamp": "0:03-0:08", "visual": "...", "voiceover": "...", "text_overlay": "..."}],\n'
                '    "cta": "...",\n'
                f'    "duration_seconds": {req.reel_duration},\n'
                '    "music_mood": "upbeat/dramatic/chill/motivational",\n'
                '    "text_overlays": ["overlay1", "overlay2"]\n'
                "  },\n"
                '  "caption": {"text": "...", "hashtags": ["#tag1", ...]}\n'
                "}"
            )),
            HumanMessage(content=f"Topic: {req.topic}"),
        ]

        response = self.llm.invoke(messages)
        parsed = json.loads(_strip_fences(response.content))

        reel_data = parsed["reel_script"]
        segments = [
            ReelSegment(
                timestamp=s["timestamp"],
                visual=s["visual"],
                voiceover=s["voiceover"],
                text_overlay=s["text_overlay"],
            )
            for s in reel_data.get("segments", [])
        ]

        reel_script = ReelScript(
            hook=reel_data["hook"],
            segments=segments,
            cta=reel_data.get("cta", ""),
            duration_seconds=reel_data.get("duration_seconds", req.reel_duration),
            music_mood=reel_data.get("music_mood", "upbeat"),
            text_overlays=reel_data.get("text_overlays", []),
        )

        caption_data = parsed["caption"]
        caption = InstagramCaption(
            text=caption_data["text"],
            hashtags=caption_data.get("hashtags", []),
        )

        result = InstagramResponse(
            reel_script=reel_script,
            caption=caption,
            topic=req.topic,
            event_context=req.event_context,
        )

        if self.agent_logger:
            self.agent_logger.log_decision(
                decision_type=DecisionType.CONTENT_GENERATION,
                agent_name="instagram_generator",
                action=f"Generated Instagram Reel script ({req.reel_duration}s) + caption",
                rationale=f"Topic: {req.topic}, Tone: {req.tone.value}, Event: {req.event_context or 'none'}",
                input_summary=req.model_dump(mode="json"),
                output_summary={
                    "reel_duration": reel_script.duration_seconds,
                    "segments": len(segments),
                    "music_mood": reel_script.music_mood,
                    "preview": reel_script.hook,
                },
                event_context=req.event_context,
            )
            from src.models.common import Platform
            self.agent_logger.log_post(
                platform=Platform.INSTAGRAM,
                post_type="reel_script",
                content_preview=f"Hook: {reel_script.hook} | {caption.text[:150]}",
                timing_score=0.0,
                timing_rationale="Generated on demand",
                event_context=req.event_context,
            )

        return result
