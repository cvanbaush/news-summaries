"""AI-powered article summarization."""

from openai import OpenAI

from src.models import Article


class Summarizer:
    """Summarizes news articles using OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def summarize_article(self, article: Article) -> str:
        """Generate a concise summary of an article."""
        prompt = f"""Summarize this news article in 2-3 sentences. Focus on the key facts
and why it matters. Be concise and objective.

Title: {article.title}
Source: {article.source}
Content: {article.content or 'No content available'}"""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    def summarize_batch(self, articles: list[Article]) -> list[Article]:
        """Summarize a batch of articles."""
        for article in articles:
            if article.content:
                article.summary = self.summarize_article(article)
        return articles

    def generate_digest_intro(self, article_count: int) -> str:
        """Generate an intro paragraph for the digest."""
        prompt = f"""Write a brief, one-sentence introduction for a news digest
containing {article_count} articles covering world, national, and local news.
Keep it professional and neutral."""

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content
