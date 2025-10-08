"""Helpers for interacting with the OpenRouter API."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class OpenRouterResponse:
    """Lightweight container for the relevant portion of an OpenRouter reply."""

    content: str
    raw: dict


class OpenRouterError(RuntimeError):
    """Raised when the OpenRouter API cannot be reached or returns an error."""


def call_openrouter(
    prompt: str,
    *,
    api_key: Optional[str] = None,
    model: str = "openrouter/anthropic/claude-3.5-sonnet",
    temperature: float = 0.2,
) -> OpenRouterResponse:
    """Call the OpenRouter chat completions endpoint and return the first message."""

    key = api_key or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise OpenRouterError("OPENROUTER_API_KEY must be provided to call OpenRouter")

    payload = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": temperature,
        }
    ).encode("utf-8")

    request = Request(
        OPENROUTER_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "HTTP-Referer": "https://github.com/openai/llm_ipl",
            "X-Title": "uoa-toolkit",
        },
        method="POST",
    )

    try:
        with urlopen(request) as response:  # nosec B310 - trusted endpoint configured by user
            body = response.read().decode("utf-8")
    except HTTPError as error:  # pragma: no cover - network failure
        raise OpenRouterError(f"OpenRouter responded with status {error.code}") from error
    except URLError as error:  # pragma: no cover - network failure
        raise OpenRouterError("Could not reach OpenRouter") from error

    parsed = json.loads(body)
    try:
        message = parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as error:
        raise OpenRouterError("Unexpected OpenRouter response structure") from error

    return OpenRouterResponse(content=message, raw=parsed)


def democratic_peace_prompt() -> str:
    """Construct a prompt that asks the LLM for a democratic peace recipe."""

    return (
        "You are configuring a unit-of-analysis data pipeline for political science. "
        "Provide ONLY a YAML recipe (no markdown fences) that can be consumed by a toolkit "
        "to test the democratic peace theory. The YAML should include:\n"
        "name, description, uoa, datasets, and output sections.\n"
        "Assume CSV inputs describing dyad-year observations live under a directory named "
        "'democratic_peace' relative to a provided data root.\n"
        "Ensure the recipe joins: a dyad-year base population, observed militarized disputes, "
        "and an indicator of joint democracy.\n"
        "Use join_keys of ['dyad_id', 'year'] throughout and suggest exporting to Excel and CSV."
    )
