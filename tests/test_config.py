"""Tests for core.config — provider configuration loading/saving."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.config import ProviderConfig, load_config, save_config


class TestSaveAndLoad:
    def test_round_trip(self, tmp_path: Path) -> None:
        cfg = ProviderConfig(
            api_key="sk-or-v1-test123",
            base_url="https://openrouter.ai/api/v1",
            default_model="anthropic/claude-sonnet-4",
        )
        config_file = tmp_path / "config.toml"
        save_config(cfg, config_file)

        loaded = load_config(config_file)
        assert loaded.api_key == cfg.api_key
        assert loaded.base_url == cfg.base_url
        assert loaded.default_model == cfg.default_model

    def test_file_permissions(self, tmp_path: Path) -> None:
        cfg = ProviderConfig(api_key="sk-or-v1-test")
        config_file = tmp_path / "config.toml"
        save_config(cfg, config_file)
        mode = config_file.stat().st_mode & 0o777
        assert mode == 0o600

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="vibecheck auth"):
            load_config(tmp_path / "nonexistent.toml")

    def test_defaults_applied(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            '[provider]\napi_key = "sk-or-v1-minimal"\n',
            encoding="utf-8",
        )
        loaded = load_config(config_file)
        assert loaded.api_key == "sk-or-v1-minimal"
        assert loaded.base_url == "https://openrouter.ai/api/v1"
        assert loaded.default_model == "anthropic/claude-sonnet-4"
