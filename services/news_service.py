

from models.news import NewsAdd
from repositories.news_repository import NewsRepository
from utils.summurizer_utils import MultilingualSummarizer


class NewsService:
    
    repository: NewsRepository
    
    def __init__(self) -> None:
        self.repository = NewsRepository()
        
    def add_news(self, news: NewsAdd) -> None:
        news.body = MultilingualSummarizer().summarize(news.body)['summary']
        self.repository.add_news(news);   