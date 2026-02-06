"""News source fetchers."""

from .newsapi import NewsAPIFetcher
from .rss import RSSFetcher

__all__ = ["RSSFetcher", "NewsAPIFetcher"]
