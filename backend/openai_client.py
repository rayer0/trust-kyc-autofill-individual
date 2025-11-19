"""Utilities for turning unstructured text into ClientProfile instances."""
from __future__ import annotations

import json
import os
from typing import Dict

from openai import OpenAI

from .models import ClientProfile

SYSTEM_PROMPT = """You are a compliance analyst that extracts structured KYC data from messy text.
Return valid JSON matching the provided Pydantic schema. Use null for unknown values."""


class OpenAIProfileGenerator:
    """Wrapper around the OpenAI Responses API to produce ClientProfile objects."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        self._client = OpenAI(api_key=api_key)

    def generate_profile(self, text: str, hints: Dict[str, str] | None = None) -> ClientProfile:
        payload = {
            "text": text,
            "hints": hints or {},
        }
        response = self._client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract a ClientProfile from the following information:",
                        },
                        {"type": "json_schema", "json_schema": ClientProfile.model_json_schema()},
                        {"type": "text", "text": json.dumps(payload)},
                    ],
                },
            ],
            response_format={"type": "json_schema", "json_schema": ClientProfile.model_json_schema()},
        )

        content = response.output[0].content[0].text  # type: ignore[index]
        data = json.loads(content)
        return ClientProfile(**data)


__all__ = ["OpenAIProfileGenerator"]
