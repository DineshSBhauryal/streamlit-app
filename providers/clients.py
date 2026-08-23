from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

class ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class Provider:
    label: str
    key_label: str
    key_placeholder: str
    model: str


PROVIDERS = {
    "anthropic": Provider("Claude", "Anthropic API key", "sk-ant-...", "claude-3-5-sonnet-latest"),
    "openai": Provider("OpenAI", "OpenAI API key", "sk-...", "gpt-4o-mini"),
    "xai": Provider("Grok", "xAI API key", "xai-...", "grok-3-mini"),
}


class BaseProviderClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def explain(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError

    @staticmethod
    def _request(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=90)
        except requests.RequestException as error:
            raise ProviderError(f"Could not reach the provider: {error}") from error
        if not response.ok:
            try:
                error_body = response.json()
                error_value = error_body.get("error") if isinstance(error_body, dict) else None
                if isinstance(error_value, dict):
                    detail = error_value.get("message") or response.text
                elif error_value:
                    detail = str(error_value)
                else:
                    detail = response.text
            except ValueError:
                detail = response.text
            raise ProviderError(f"Provider request failed ({response.status_code}): {detail}")
        return response.json()


class OpenAIClient(BaseProviderClient):
    def explain(self, messages: list[dict[str, str]]) -> str:
        data = self._request(
            "https://api.openai.com/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {"model": self.model, "messages": messages, "temperature": 0.4},
        )
        return data["choices"][0]["message"]["content"]


class XAIClient(OpenAIClient):
    def explain(self, messages: list[dict[str, str]]) -> str:
        data = self._request(
            "https://api.x.ai/v1/chat/completions",
            {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            {"model": self.model, "messages": messages, "temperature": 0.4},
        )
        return data["choices"][0]["message"]["content"]


class AnthropicClient(BaseProviderClient):
    def explain(self, messages: list[dict[str, str]]) -> str:
        system_message, user_message = messages
        data = self._request(
            "https://api.anthropic.com/v1/messages",
            {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            {
                "model": self.model,
                "max_tokens": 1800,
                "system": system_message["content"],
                "messages": [user_message],
            },
        )
        return "\n".join(block["text"] for block in data["content"] if block.get("type") == "text")


def create_provider(provider_id: str, api_key: str) -> BaseProviderClient:
    provider = PROVIDERS[provider_id]
    client_type = {"anthropic": AnthropicClient, "openai": OpenAIClient, "xai": XAIClient}[provider_id]
    return client_type(api_key, provider.model)
