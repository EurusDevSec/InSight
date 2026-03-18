"""
LLM client for the RAG pipeline (OpenAI-compatible).

Task 3.2.1 — Uses Google Gemini API (free tier) via OpenAI-compatible endpoint.
Also supports Ollama, vLLM, and any OpenAI-compatible API.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"  # Gemini OpenAI-compatible
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.3  # low temp for medical accuracy


@dataclass
class LLMClient:
    """OpenAI-compatible LLM client.

    Default: Google Gemini API (free tier).
    Also works with Ollama, vLLM, LM Studio, or any OpenAI-compatible API.
    """

    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    api_key: str = ""  # Set via GEMINI_API_KEY env var
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE
    _client: object | None = field(default=None, init=False, repr=False)

    def connect(self) -> None:
        """Initialise the underlying HTTP client."""
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "openai package is not installed. Run: pip install openai"
            )

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        logger.info(
            "LLM client connected: model=%s, base_url=%s",
            self.model,
            self.base_url,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Send a chat completion request and return the assistant's reply.

        Args:
            system_prompt: System-level instructions for the LLM.
            user_prompt: User query / context-augmented prompt.

        Returns:
            The assistant's text response.

        Raises:
            RuntimeError: If :meth:`connect` has not been called.
        """
        if self._client is None:
            raise RuntimeError("Client not connected. Call connect() first.")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        logger.debug(
            "LLM request: model=%s, tokens=%d, temp=%.1f",
            self.model,
            self.max_tokens,
            self.temperature,
        )

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        text = response.choices[0].message.content or ""
        logger.debug("LLM response length: %d chars", len(text))
        return text.strip()

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> dict:
        """Like :meth:`generate`, but parse the response as JSON.

        Falls back to wrapping raw text in ``{"advice": text}`` on parse
        failure.
        """
        raw = self.generate(system_prompt, user_prompt)
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("LLM did not return valid JSON; wrapping raw text.")
            return {"advice": raw}
