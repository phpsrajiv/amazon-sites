import os
import json
import re
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.models.linkedin import (
    LinkedInRequest,
    LinkedInResponse,
    LinkedInTextPost,
    LinkedInPoll,
)
from src.models.logging import DecisionType

logger = logging.getLogger(__name__)


def _strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


class LinkedInPostGenerator:

    def __init__(self, agent_logger=None):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=0.6,
        )
        self.agent_logger = agent_logger

    def generate(self, req: LinkedInRequest) -> LinkedInResponse:
        event_ctx = ""
        if req.event_context:
            event_ctx = f"\nEvent context: {req.event_context}. Reference this event naturally."

        poll_instruction = ""
        if req.include_poll:
            poll_instruction = (
                '\n\nAlso generate a LinkedIn poll related to the topic:\n'
                '{"question": "...", "options": ["Option A", "Option B", "Option C", "Option D"], "context_text": "..."}\n'
                "Poll should have 2-4 options. Include it as a 'poll' key in the response."
            )

        messages = [
            SystemMessage(content=(
                "You are an expert LinkedIn content strategist for Amazon sellers and D2C brands in India. "
                f"Brand: {req.brand}.\n\n"
                "Generate a professional LinkedIn text post:\n"
                "- Start with a strong hook line (1 sentence that grabs attention)\n"
                "- Body: 150-250 words, insightful, professional\n"
                "- Include 3-5 relevant hashtags\n"
                "- End with a clear CTA\n"
                "- Do NOT use carousel format (text post only)\n\n"
                f"Tone: {req.tone.value}\n"
                f"{event_ctx}\n"
                f"{poll_instruction}\n\n"
                "Respond in JSON:\n"
                "{\n"
                '  "text_post": {"hook_line": "...", "body": "...", "hashtags": ["#tag1", ...], "cta": "..."},\n'
                '  "poll": null or {"question": "...", "options": [...], "context_text": "..."}\n'
                "}"
            )),
            HumanMessage(content=f"Topic: {req.topic}"),
        ]

        response = self.llm.invoke(messages)
        parsed = json.loads(_strip_fences(response.content))

        text_post_data = parsed["text_post"]
        text_post = LinkedInTextPost(
            hook_line=text_post_data["hook_line"],
            body=text_post_data["body"],
            hashtags=text_post_data.get("hashtags", []),
            cta=text_post_data.get("cta", ""),
        )

        poll = None
        if parsed.get("poll"):
            poll_data = parsed["poll"]
            poll = LinkedInPoll(
                question=poll_data["question"],
                options=poll_data["options"],
                context_text=poll_data.get("context_text", ""),
            )

        result = LinkedInResponse(
            text_post=text_post,
            poll=poll,
            topic=req.topic,
            event_context=req.event_context,
        )

        if self.agent_logger:
            self.agent_logger.log_decision(
                decision_type=DecisionType.CONTENT_GENERATION,
                agent_name="linkedin_post_generator",
                action=f"Generated LinkedIn text post{' + poll' if poll else ''}",
                rationale=f"Topic: {req.topic}, Tone: {req.tone.value}, Event: {req.event_context or 'none'}",
                input_summary=req.model_dump(mode="json"),
                output_summary={"has_poll": poll is not None, "preview": text_post.hook_line},
                event_context=req.event_context,
            )
            from src.models.common import Platform
            self.agent_logger.log_post(
                platform=Platform.LINKEDIN,
                post_type="linkedin_text_post",
                content_preview=f"{text_post.hook_line} {text_post.body[:150]}",
                timing_score=0.0,
                timing_rationale="Generated on demand",
                event_context=req.event_context,
            )

        return result
