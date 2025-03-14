from pygooglenews import GoogleNews
from app.models.schemas import Article, NewsResponse
import logging

logger = logging.getLogger(__name__)

def fetch_google_news(category: str, lang: str, country: str, limit: int) -> NewsResponse:
    try:
        logger.info(f"Fetching trends: category={category}, lang={lang}, country={country}, limit={limit}")
        gn = GoogleNews(lang=lang, country=country)
        news_feed = gn.topic_headlines(category.upper())

        articles = []
        for entry in news_feed["entries"][:limit]:
            title = entry["title"].split(" - ")[0].strip()
            articles.append(
                Article(
                    title=title,
                    link=entry["link"],
                    published=entry["published"],
                    source=entry["source"]["title"]
                )
            )

        return NewsResponse(feed_title=news_feed["feed"].title, articles=articles)
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        raise Exception(f"Error fetching news: {str(e)}")

def fetch_trends_by_topic(
    topic_name: str,
    lang: str = "en",
    country: str = "WORLD",
    limit: int = 10
) -> NewsResponse:
    try:
        logger.info(f"Fetching trends for topic '{topic_name}' with lang={lang}, country={country}, limit={limit}")
        gn = GoogleNews(lang=lang, country=country)
        search_results = gn.search(query=topic_name)
        if not isinstance(search_results, dict) or "entries" not in search_results or not search_results["entries"]:
            logger.warning(f"No news data available for topic '{topic_name}'")
            raise Exception("No news data available for the given topic and parameters.")

        articles = []
        for entry in search_results["entries"][:limit]:
            if not all(key in entry for key in ["title", "link", "published", "source"]):
                logger.warning(f"Skipping malformed entry: {entry}")
                continue
            title = entry["title"].split(" - ")[0].strip()
            articles.append(
                Article(
                    title=title,
                    link=entry["link"],
                    published=entry["published"],
                    source=entry["source"]["title"]
                )
            )

        if not articles:
            logger.warning(f"No valid articles found for topic '{topic_name}'")
            raise Exception("No valid articles found for the given topic and parameters.")

        return NewsResponse(
            feed_title=search_results["feed"].title,
            articles=articles
        )
    except Exception as e:
        logger.error(f"Error fetching topic trends for '{topic_name}': {str(e)}")
        raise Exception(f"Error fetching news: {str(e)}")