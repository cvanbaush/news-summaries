"""Main entry point for the news summarization service."""

from datetime import datetime, timezone

from src.agent import Summarizer
from src.config import settings
from src.dedup import deduplicate_articles
from src.models import Category, NewsDigest
from src.output import MarkdownFormatter
from src.sources import NewsAPIFetcher


def fetch_all_articles(fetcher: NewsAPIFetcher) -> dict[Category, list]:
    """Fetch articles from NewsAPI."""
    articles = {
        Category.WORLD: [],
        Category.NATIONAL: [],
        Category.LOCAL: [],
    }

    # Fetch world news
    print("  Fetching world news...")
    articles[Category.WORLD] = fetcher.fetch_top_headlines(
        category=Category.WORLD,
        country="us",  # Gets general/international coverage
        page_size=10,
    )

    # Fetch national news
    print("  Fetching national news...")
    articles[Category.NATIONAL] = fetcher.fetch_top_headlines(
        category=Category.NATIONAL,
        country="us",
        page_size=10,
    )

    # Fetch local news (using search query)
    # Uncomment and customize for your location
    # print("  Fetching local news...")
    # articles[Category.LOCAL] = fetcher.fetch_everything(
    #     query="San Francisco",
    #     category=Category.LOCAL,
    #     page_size=10,
    # )

    return articles


def main():
    """Run the news summarization pipeline."""
    if not settings.newsapi_key:
        print("Error: NEWS_NEWSAPI_KEY environment variable is required")
        print("Get your free API key at https://newsapi.org")
        return

    print("Fetching articles from NewsAPI...")
    with NewsAPIFetcher(api_key=settings.newsapi_key) as fetcher:
        articles = fetch_all_articles(fetcher)

    total = sum(len(a) for a in articles.values())
    print(f"Found {total} articles")

    # Deduplicate across categories
    articles = deduplicate_articles(articles)
    deduped_total = sum(len(a) for a in articles.values())
    print(f"After deduplication: {deduped_total} unique articles")

    # Limit articles per category
    max_per_category = 5
    for category in articles:
        articles[category] = articles[category][:max_per_category]

    # Summarize if API key is available
    if settings.openai_api_key:
        print("Summarizing articles...")
        summarizer = Summarizer(api_key=settings.openai_api_key)
        for category in articles:
            articles[category] = summarizer.summarize_batch(articles[category])
    else:
        print("No OpenAI API key found - skipping summarization")
        print("Set NEWS_OPENAI_API_KEY environment variable to enable")

    # Create digest
    digest = NewsDigest(
        generated_at=datetime.now(timezone.utc),
        articles=articles,
    )

    # Format output
    formatter = MarkdownFormatter()
    output = formatter.format(digest)

    # Write to file
    output_file = "digest.md"
    with open(output_file, "w") as f:
        f.write(output)

    print(f"Digest written to {output_file}")


if __name__ == "__main__":
    main()
