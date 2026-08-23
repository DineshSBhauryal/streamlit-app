from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

class ProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelOption:
    model_id: str
    input_price: float | None = None
    output_price: float | None = None

    @property
    def label(self) -> str:
        if self.input_price is None or self.output_price is None:
            return f"{self.model_id} · pricing unavailable from provider"
        return (
            f"{self.model_id} · ${self.input_price:g} input / "
            f"${self.output_price:g} output per 1M tokens"
        )


@dataclass(frozen=True)
class Provider:
    label: str
    key_label: str
    key_placeholder: str
    models_url: str
    pricing_prefix: str


PROVIDERS = {
    "anthropic": Provider("Claude", "Anthropic API key", "sk-ant-...", "https://api.anthropic.com/v1/models", "anthropic/"),
    "openai": Provider("OpenAI", "OpenAI API key", "sk-...", "https://api.openai.com/v1/models", "openai/"),
    "xai": Provider("Grok", "xAI API key", "xai-...", "https://api.x.ai/v1/models", "x-ai/"),
}


class BaseProviderClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def explain(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError

    @staticmethod
    def _get(url: str, headers: dict[str, str]) -> dict[str, Any]:
        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.RequestException as error:
            raise ProviderError(f"Could not reach the provider: {error}") from error
        if not response.ok:
            try:
                error_body = response.json()
                error_value = error_body.get("error") if isinstance(error_body, dict) else None
                detail = error_value.get("message") if isinstance(error_value, dict) else str(error_value or response.text)
            except ValueError:
                detail = response.text
            raise ProviderError(f"Provider verification failed ({response.status_code}): {detail}")
        return response.json()

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
            if response.status_code == 404 and "model" in detail.lower():
                detail = f"The selected model is unavailable: {detail} Choose another model from the dropdown."
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


def list_available_models(provider_id: str, api_key: str) -> tuple[ModelOption, ...]:
    provider = PROVIDERS[provider_id]
    headers = {"Authorization": f"Bearer {api_key}"}
    if provider_id == "anthropic":
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}

    data = BaseProviderClient._get(provider.models_url, headers)
    models = []
    for item in data.get("data", []):
        if not isinstance(item, dict) or not item.get("id"):
            continue
        pricing = item.get("pricing", {})
        models.append(
            ModelOption(
                item["id"],
                _price_per_million(pricing.get("input")) if isinstance(pricing, dict) else None,
                _price_per_million(pricing.get("output")) if isinstance(pricing, dict) else None,
            )
        )
    if not models:
        raise ProviderError(f"{provider.label} returned no available models.")
    return tuple(sorted(_add_pricing(provider, models), key=lambda option: option.model_id))


def _price_per_million(value: Any) -> float | None:
    try:
        return float(value) * 1_000_000 if value is not None else None
    except (TypeError, ValueError):
        return None


def _add_pricing(provider: Provider, models: list[ModelOption]) -> list[ModelOption]:
    try:
        pricing_data = BaseProviderClient._get("https://openrouter.ai/api/v1/models", {})
    except ProviderError:
        return models

    pricing_by_id = {
        item.get("id"): item.get("pricing", {})
        for item in pricing_data.get("data", [])
        if isinstance(item, dict) and item.get("id", "").startswith(provider.pricing_prefix)
    }
    enriched = []
    for model in models:
        pricing = pricing_by_id.get(f"{provider.pricing_prefix}{model.model_id}", {})
        enriched.append(
            ModelOption(
                model.model_id,
                model.input_price or _price_per_million(pricing.get("prompt")),
                model.output_price or _price_per_million(pricing.get("completion")),
            )
        )
    return enriched


def create_provider(provider_id: str, api_key: str, model: str) -> BaseProviderClient:
    provider = PROVIDERS[provider_id]
    client_type = {"anthropic": AnthropicClient, "openai": OpenAIClient, "xai": XAIClient}[provider_id]
    return client_type(api_key, model)
