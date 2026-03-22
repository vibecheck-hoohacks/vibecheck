"""Thin wrapper around OpenAI client for OpenRouter integration."""

from __future__ import annotations

from openai import OpenAI

from core.config import ProviderConfig, load_config


def get_client(config: ProviderConfig | None = None) -> OpenAI:
    """Create an OpenAI client pointed at the configured provider (default: OpenRouter)."""
    cfg = config or load_config()
    return OpenAI(base_url=cfg.base_url, api_key=cfg.api_key)
