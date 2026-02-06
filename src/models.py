"""Data models for the news summarization service."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl


class Category(str, Enum):
    WORLD = "world"
    NATIONAL = "national"
    LOCAL = "local"


class Article(BaseModel):
    """Represents a news article."""

    title: str
    url: HttpUrl
    source: str
    category: Category
    published: datetime | None = None
    content: str | None = None
    summary: str | None = None

    def __hash__(self) -> int:
        return hash(self.url)


class NewsDigest(BaseModel):
    """A collection of summarized articles."""

    generated_at: datetime
    articles: dict[Category, list[Article]]

    @property
    def total_articles(self) -> int:
        return sum(len(arts) for arts in self.articles.values())
