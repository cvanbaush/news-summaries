"""RSS feed fetcher."""

from datetime import datetime, timezone

import feedparser

from src.config import SourceConfig
from src.models import Article, Category


class RSSFetcher:
    """Fetches articles from RSS feeds."""

    def fetch(self, source: SourceConfig, category: Category) -> list[Article]:
        """Fetch articles from an RSS feed."""
        if not source.enabled:
            return []

        feed = feedparser.parse(source.url)
        articles = []

        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            article = Article(
                title=entry.get("title", "No title"),
                url=entry.get("link", ""),
                source=source.name,
                category=category,
                published=published,
                content=entry.get("summary", ""),
            )
            articles.append(article)

        return articles
