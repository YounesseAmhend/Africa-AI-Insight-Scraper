from constants import TRIGGER_WORDS_CATEGORIES
from models.news import NewsAdd
from repositories.category_repository import CategoryRepository
from repositories.news_repository import NewsRepository
from utils.logger import logger
from utils.summurizer_utils import MultilingualSummarizer


class NewsService:
    news_repository: NewsRepository
    category_repository: CategoryRepository

    def __init__(self) -> None:
        self.news_repository = NewsRepository()
        self.category_repository = CategoryRepository()

    def add_news(self, news: NewsAdd) -> None:
        logger.info("Starting category detection for news article")
        for key, values in TRIGGER_WORDS_CATEGORIES.items():
            logger.debug(f"Checking category: {key}")
            for value in values:
                if value in news.body:
                    logger.info(f"Found trigger word '{value}' for category '{key}'")
                    news.categoryId = self.category_repository.get_or_create_category(
                        key
                    )
                    logger.info(f"Assigned category ID: {news.categoryId}")
                    break
            if news.categoryId:
                break
        if news.categoryId is None:
            news.categoryId = self.category_repository.get_or_create_category(
                "Uncategorized"
            )
        logger.info("Starting summarization of news article")
        summary_result = MultilingualSummarizer().summarize(news.body)
        if "<body>" in summary_result:
            body_start = summary_result.find("<body>") + len("<body>")
            body_end = summary_result.find("</body>")
            body_content = summary_result[body_start:body_end].strip()
        else:
            body_content = summary_result

        # Handle [IMAGE HERE] tags
        if news.imageUrl:
            # Replace first [IMAGE HERE] with actual image tag
            body_content = body_content.replace(
                "[IMAGE HERE]",
                f'<img class="image-placeholder" src="{news.imageUrl}" />',
                1,
            )
        # Remove any remaining [IMAGE HERE] tags
        body_content = body_content.replace("[IMAGE HERE]", "")
        body_content = body_content.replace('<div class="image-placeholder"></div>', "")
        news.body = body_content
        logger.info(f"Summary generated: {news.body[:100]}...")

        logger.info("Adding news article to repository")
        self.news_repository.add_news(news)
        logger.info("Successfully added news article")
