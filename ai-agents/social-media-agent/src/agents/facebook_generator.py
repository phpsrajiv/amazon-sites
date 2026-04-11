import os
import json
import re
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.models.facebook import FacebookRequest, FacebookResponse, FacebookPost
from src.models.common import ContentTone
from src.models.logging import DecisionType

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


class FacebookGenerator:

    def __init__(self, agent_logger=None):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=0.7,
        )
        self.agent_logger = agent_logger

    def generate(self, req: FacebookRequest) -> FacebookResponse:
        event_ctx = ""
        if req.event_context:
            event_ctx = f"\nEvent context: {req.event_context}. Weave this naturally into the posts with festive/sale-specific language."

        messages = [
            SystemMessage(content=(
                "You are an expert social media copywriter for Amazon sellers and D2C brands in India. "
                f"Brand: {req.brand}.\n\n"
                "Generate Facebook post variants. Each post should:\n"
                "- Be conversational and engaging (150-300 words)\n"
                "- Use 2-4 relevant emojis naturally\n"
                "- End with a question to drive comments\n"
                "- Include 3-5 relevant hashtags\n"
                "- Include a Canva image prompt suggestion\n\n"
                f"Tone: {req.tone.value}\n"
                f"Number of variants: {req.num_variants}\n"
                f"{event_ctx}\n\n"
                "Respond in JSON:\n"
                "[\n"
                '  {"text": "...", "hashtags": ["#tag1", ...], "engagement_question": "...", '
                '"image_prompt": "...", "tone": "' + req.tone.value + '"}\n'
                "]"
            )),
            HumanMessage(content=f"Topic: {req.topic}"),
        ]

        response = self.llm.invoke(messages)
        parsed = json.loads(_strip_fences(response.content))

        variants = []
        for item in parsed:
            variants.append(FacebookPost(
                text=item["text"],
                hashtags=item.get("hashtags", []),
                engagement_question=item.get("engagement_question", ""),
                image_prompt=item.get("image_prompt", ""),
                tone=ContentTone(item.get("tone", req.tone.value)),
            ))

        result = FacebookResponse(
            variants=variants,
            topic=req.topic,
            event_context=req.event_context,
        )

        if self.agent_logger:
            self.agent_logger.log_decision(
                decision_type=DecisionType.CONTENT_GENERATION,
                agent_name="facebook_generator",
                action=f"Generated {len(variants)} Facebook post variants",
                rationale=f"Topic: {req.topic}, Tone: {req.tone.value}, Event: {req.event_context or 'none'}",
                input_summary=req.model_dump(mode="json"),
                output_summary={"variant_count": len(variants), "preview": variants[0].text[:200] if variants else ""},
                platform=None,
                event_context=req.event_context,
            )
            from src.models.common import Platform
            for v in variants:
                self.agent_logger.log_post(
                    platform=Platform.FACEBOOK,
                    post_type="facebook_post",
                    content_preview=v.text[:200],
                    timing_score=0.0,
                    timing_rationale="Generated on demand",
                    event_context=req.event_context,
                )

        return result
