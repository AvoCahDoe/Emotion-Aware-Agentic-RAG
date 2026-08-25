"""DeepSeek chat completion via OpenAI-compatible API."""

from __future__ import annotations

import os

from openai import OpenAI


DEFAULT_MODEL = "deepseek-v4-flash"
BASE_URL = "https://api.deepseek.com"


class Generator:
    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = BASE_URL,
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model or os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
        self.base_url = base_url
        self._client: OpenAI | None = None

    def load(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is not set. Add it to the environment before generating answers."
            )
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    @property
    def ready(self) -> bool:
        return bool(self.api_key)

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.4,
    ) -> str:
        self.load()
        assert self._client is not None
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return (content or "").strip()
