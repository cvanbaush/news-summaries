"""Article deduplication utilities."""

from typing import Dict, List
from urllib.parse import urlparse

from src.models import Article, Category


def normalize_url(url: str) -> str:
    """Normalize URL for comparison by removing query params and fragments."""
    parsed = urlparse(str(url))
    return f"{parsed.netloc}{parsed.path}".rstrip("/").lower()


def normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    # Remove common suffixes like "- Source Name"
    if " - " in title:
        title = title.rsplit(" - ", 1)[0]
    if " | " in title:
        title = title.rsplit(" | ", 1)[0]
    return title.strip().lower()


def deduplicate_articles(
    articles: Dict[Category, List[Article]],
) -> Dict[Category, List[Article]]:
    """Remove duplicate articles across all categories.

    Prioritizes keeping articles in this order: WORLD > NATIONAL > LOCAL.
    Duplicates are identified by normalized URL or similar title.
    """
    seen_urls: set = set()
    seen_titles: set = set()
    result: Dict[Category, List[Article]] = {cat: [] for cat in Category}

    # Process in priority order
    priority_order = [Category.WORLD, Category.NATIONAL, Category.LOCAL]

    for category in priority_order:
        for article in articles.get(category, []):
            norm_url = normalize_url(str(article.url))
            norm_title = normalize_title(article.title)

            # Skip if we've seen this URL or very similar title
            if norm_url in seen_urls:
                continue
            if norm_title in seen_titles:
                continue

            seen_urls.add(norm_url)
            seen_titles.add(norm_title)
            result[category].append(article)

    return result
