"""Configuration management."""

from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(env_prefix="NEWS_")

    openai_api_key: str = ""
    newsapi_key: str = ""
    config_dir: Path = Path(__file__).parent.parent / "config"


class SourceConfig(BaseModel):
    """A single news source configuration."""

    name: str
    url: str
    type: str = "rss"
    enabled: bool = True


class SourcesConfig(BaseModel):
    """All news sources grouped by category."""

    world: list[SourceConfig] = []
    national: list[SourceConfig] = []
    local: list[SourceConfig] = []


def load_sources(config_dir: Path) -> SourcesConfig:
    """Load news sources from YAML configuration."""
    sources_file = config_dir / "sources.yaml"
    with open(sources_file) as f:
        data = yaml.safe_load(f)

    sources_data = data.get("sources", {})
    return SourcesConfig(
        world=[SourceConfig(**s) for s in sources_data.get("world", [])],
        national=[SourceConfig(**s) for s in sources_data.get("national", [])],
        local=[SourceConfig(**s) for s in sources_data.get("local", [])],
    )


settings = Settings()
