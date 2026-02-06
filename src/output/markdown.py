"""Markdown output formatter."""

from datetime import datetime

from src.models import Category, NewsDigest


class MarkdownFormatter:
    """Formats news digest as Markdown."""

    CATEGORY_TITLES = {
        Category.WORLD: "World News",
        Category.NATIONAL: "National News",
        Category.LOCAL: "Local News",
    }

    def format(self, digest: NewsDigest, intro: str | None = None) -> str:
        """Format a news digest as Markdown."""
        lines = [
            f"# News Digest",
            f"*Generated: {digest.generated_at.strftime('%B %d, %Y at %I:%M %p')}*",
            "",
        ]

        if intro:
            lines.extend([intro, ""])

        lines.append("---")
        lines.append("")

        for category in [Category.WORLD, Category.NATIONAL, Category.LOCAL]:
            articles = digest.articles.get(category, [])
            if not articles:
                continue

            lines.append(f"## {self.CATEGORY_TITLES[category]}")
            lines.append("")

            for article in articles:
                lines.append(f"### {article.title}")
                lines.append(f"*{article.source}*")
                lines.append("")
                if article.summary:
                    lines.append(article.summary)
                lines.append("")
                lines.append(f"[Read more]({article.url})")
                lines.append("")

        return "\n".join(lines)
