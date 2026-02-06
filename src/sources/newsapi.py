"""NewsAPI fetcher."""

from datetime import datetime, timezone

import httpx

from src.models import Article, Category


class NewsAPIFetcher:
    """Fetches articles from NewsAPI.org."""

    BASE_URL = "https://newsapi.org/v2"

    # Mapping of our categories to NewsAPI categories
    CATEGORY_MAP = {
        Category.WORLD: "general",
        Category.NATIONAL: "general",
        Category.LOCAL: "general",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)

    def fetch_top_headlines(
        self,
        category: Category,
        country: str = "us",
        page_size: int = 10,
    ) -> list[Article]:
        """Fetch top headlines for a category."""
        params = {
            "apiKey": self.api_key,
            "category": self.CATEGORY_MAP.get(category, "general"),
            "country": country,
            "pageSize": page_size,
        }

        response = self.client.get(f"{self.BASE_URL}/top-headlines", params=params)
        response.raise_for_status()
        data = response.json()

        return self._parse_articles(data.get("articles", []), category)

    def fetch_everything(
        self,
        query: str,
        category: Category,
        page_size: int = 10,
    ) -> list[Article]:
        """Search for articles matching a query."""
        params = {
            "apiKey": self.api_key,
            "q": query,
            "pageSize": page_size,
            "sortBy": "publishedAt",
            "language": "en",
        }

        response = self.client.get(f"{self.BASE_URL}/everything", params=params)
        response.raise_for_status()
        data = response.json()

        return self._parse_articles(data.get("articles", []), category)

    def _parse_articles(self, raw_articles: list[dict], category: Category) -> list[Article]:
        """Parse raw API response into Article objects."""
        articles = []

        for item in raw_articles:
            published = None
            if item.get("publishedAt"):
                try:
                    published = datetime.fromisoformat(
                        item["publishedAt"].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            # Skip articles with missing essential data
            if not item.get("url") or not item.get("title"):
                continue

            # NewsAPI sometimes returns "[Removed]" for blocked content
            if item.get("title") == "[Removed]":
                continue

            article = Article(
                title=item["title"],
                url=item["url"],
                source=item.get("source", {}).get("name", "Unknown"),
                category=category,
                published=published,
                content=item.get("description") or item.get("content") or "",
            )
            articles.append(article)

        return articles

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
