import requests
from bs4 import BeautifulSoup
import newspaper
from newspaper import Article
import pandas as pd
import logging
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable
import hashlib
import sqlite3
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@dataclass
class ArticleData:
    url: str
    title: str
    text: str
    publish_date: Optional[str]
    authors: List[str]
    summary: str
    keywords: List[str]
    source: str
    category: str
    image_url: Optional[str]
    html: str
    article_hash: str

class SiteConfig:
    """Configuration for a specific website"""
    
    def __init__(self, site_name: str, base_url: str, ai_news_url: str, 
                 article_selector: str, title_selector: Optional[str] = None,
                 date_selector: Optional[str] = None, author_selector: Optional[str] = None,
                 content_selector: Optional[str] = None, category: str = "ai-news",
                 use_newspaper: bool = True, custom_parser: Optional[Callable] = None):
        self.site_name = site_name
        self.base_url = base_url
        self.ai_news_url = ai_news_url
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.date_selector = date_selector
        self.author_selector = author_selector
        self.content_selector = content_selector
        self.category = category
        self.use_newspaper = use_newspaper
        self.custom_parser = custom_parser

class AINewsScraper:
    """Main scraper class orchestrating the extraction process"""
    
    def __init__(self, db_path: str = "ai_news.db", user_agent: Optional[str] = None):
        self.db_path = db_path
        self.site_configs = {}
        
        # Set up a session with rotating user agents
        self.session = requests.Session()
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.user_agent = user_agent or default_ua
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Initialize database
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create articles table if it doesn't exist
        c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            text TEXT,
            publish_date TEXT,
            authors TEXT,
            summary TEXT,
            keywords TEXT,
            source TEXT,
            category TEXT,
            image_url TEXT,
            html TEXT,
            article_hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()

    def add_site_config(self, config: SiteConfig):
        """Add a website configuration to the scraper"""
        self.site_configs[config.site_name] = config
        logger.info(f"Added configuration for site: {config.site_name}")

    def load_site_configs(self, config_file: str):
        """Load website configurations from a JSON file"""
        try:
            with open(config_file, 'r') as f:
                configs = json.load(f)
            
            for site_name, config in configs.items():
                self.add_site_config(SiteConfig(
                    site_name=site_name,
                    base_url=config.get('base_url'),
                    ai_news_url=config.get('ai_news_url'),
                    article_selector=config.get('article_selector'),
                    title_selector=config.get('title_selector'),
                    date_selector=config.get('date_selector'),
                    author_selector=config.get('author_selector'),
                    content_selector=config.get('content_selector'),
                    category=config.get('category', 'ai-news'),
                    use_newspaper=config.get('use_newspaper', True)
                ))
            logger.info(f"Loaded {len(configs)} site configurations")
        except Exception as e:
            logger.error(f"Error loading site configurations: {e}")

    def _random_delay(self, min_seconds=1, max_seconds=5):
        """Add a random delay between requests to be polite"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _extract_article_links(self, config: SiteConfig) -> List[str]:
        """Extract article links from a news listing page"""
        try:
            response = self.session.get(config.ai_news_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_elements = soup.select(config.article_selector)
            
            links = []
            for element in article_elements:
                # Find the link, which could be the element itself or a child
                if element.name == 'a':
                    link = element.get('href')
                else:
                    link_element = element.find('a')
                    try:
                        link = link_element.get('href') if link_element else None
                    except (AttributeError, TypeError):
                        continue
                
                if link:
                    # Handle relative URLs
                    link = str(link)  # Ensure link is a string
                    if link.startswith('/'):
                        link = config.base_url.rstrip('/') + link
                    links.append(link)
            
            logger.info(f"Extracted {len(links)} links from {config.site_name}")
            return links
        except Exception as e:
            logger.error(f"Error extracting links from {config.site_name}: {e}")
            return []

    def _parse_with_newspaper(self, url: str, source: str, category: str) -> Optional[ArticleData]:
        """Parse an article using the newspaper library"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()  # Extract keywords, summary
            
            # Generate a unique hash for the article content
            content_hash = hashlib.md5(article.text.encode()).hexdigest()
            
            return ArticleData(
                url=url,
                title=article.title,
                text=article.text,
                publish_date=article.publish_date.isoformat() if article.publish_date else None,
                authors=article.authors,
                summary=article.summary,
                keywords=article.keywords,
                source=source,
                category=category,
                image_url=article.top_image,
                html=article.html,
                article_hash=content_hash
            )
        except Exception as e:
            logger.error(f"Error parsing article with newspaper ({url}): {e}")
            return None

    def _parse_with_selectors(self, url: str, config: SiteConfig) -> Optional[ArticleData]:
        """Parse an article using BeautifulSoup and custom selectors"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = ""
            if config.title_selector:
                title_element = soup.select_one(config.title_selector)
                if title_element:
                    title = title_element.get_text(strip=True)
            
            # Extract date
            date_str = None
            if config.date_selector:
                date_element = soup.select_one(config.date_selector)
                if date_element:
                    date_str = date_element.get_text(strip=True)
            
            # Extract authors
            authors = []
            if config.author_selector:
                author_elements = soup.select(config.author_selector)
                authors = [a.get_text(strip=True) for a in author_elements]
            
            # Extract content
            content = ""
            if config.content_selector:
                content_elements = soup.select(config.content_selector)
                content = "\n".join([e.get_text(strip=True) for e in content_elements])
            
            # Generate a unique hash for the article content
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Create a simple summary and keywords if content exists
            summary = content[:200] + "..." if len(content) > 200 else content
            keywords = []
            
            return ArticleData(
                url=url,
                title=title,
                text=content,
                publish_date=date_str,
                authors=authors,
                summary=summary,
                keywords=keywords,
                source=config.site_name,
                category=config.category,
                image_url=None,
                html=response.text,
                article_hash=content_hash
            )
        except Exception as e:
            logger.error(f"Error parsing article with selectors ({url}): {e}")
            return None

    def _parse_article(self, url: str, config: SiteConfig) -> Optional[ArticleData]:
        """Parse an article using the appropriate method"""
        if config.custom_parser:
            return config.custom_parser(url, config)
        elif config.use_newspaper:
            return self._parse_with_newspaper(url, config.site_name, config.category)
        else:
            return self._parse_with_selectors(url, config)

    def _store_article(self, article: ArticleData):
        """Store an article in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if article already exists
            c.execute("SELECT id FROM articles WHERE article_hash = ?", (article.article_hash,))
            if c.fetchone():
                logger.info(f"Article already exists: {article.url}")
                conn.close()
                return
            
            # Insert the article
            c.execute('''
            INSERT INTO articles 
            (url, title, text, publish_date, authors, summary, keywords, source, category, image_url, html, article_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.url,
                article.title,
                article.text,
                article.publish_date,
                json.dumps(article.authors),
                article.summary,
                json.dumps(article.keywords),
                article.source,
                article.category,
                article.image_url,
                article.html,
                article.article_hash
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored article: {article.title} from {article.source}")
        except Exception as e:
            logger.error(f"Error storing article: {e}")

    def scrape_site(self, site_name: str) -> int:
        """Scrape a specific site for AI news"""
        if site_name not in self.site_configs:
            logger.error(f"No configuration found for site: {site_name}")
            return 0
        
        config = self.site_configs[site_name]
        article_count = 0
        
        try:
            # Get article links
            links = self._extract_article_links(config)
            
            # Process each article
            for link in links:
                self._random_delay()
                article = self._parse_article(link, config)
                if article:
                    self._store_article(article)
                    article_count += 1
            
            logger.info(f"Processed {article_count} articles from {site_name}")
            return article_count
        except Exception as e:
            logger.error(f"Error scraping site {site_name}: {e}")
            return 0

    def scrape_all_sites(self, max_workers: int = 4) -> Dict[str, int]:
        """Scrape all configured sites for AI news"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scrape_site, site_name): site_name 
                      for site_name in self.site_configs.keys()}
            
            for future in futures:
                site_name = futures[future]
                try:
                    article_count = future.result()
                    results[site_name] = article_count
                except Exception as e:
                    logger.error(f"Error in thread for site {site_name}: {e}")
                    results[site_name] = 0
        
        return results

    def search_articles(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for articles in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # Simple search implementation
            search_pattern = f"%{query}%"
            c.execute('''
            SELECT id, url, title, summary, source, publish_date, category
            FROM articles
            WHERE title LIKE ? OR text LIKE ? OR summary LIKE ?
            ORDER BY publish_date DESC
            LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit))
            
            results = [dict(row) for row in c.fetchall()]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []

    def export_to_csv(self, output_file: str):
        """Export all articles to a CSV file"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT id, url, title, summary, source, publish_date, category FROM articles"
            df = pd.read_sql_query(query, conn)
            df.to_csv(output_file, index=False)
            conn.close()
            logger.info(f"Exported {len(df)} articles to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

# Example site configuration file (site_configs.json)
EXAMPLE_SITE_CONFIGS = {
    "techmeme": {
        "base_url": "https://www.techmeme.com",
        "ai_news_url": "https://www.techmeme.com/search/AI",
        "article_selector": ".item",
        "use_newspaper": True,
        "category": "ai-news"
    },
    "venturebeat": {
        "base_url": "https://venturebeat.com",
        "ai_news_url": "https://venturebeat.com/category/ai/",
        "article_selector": "article.ArticleListing",
        "title_selector": "h2.ArticleListing-title",
        "use_newspaper": True,
        "category": "ai-news"
    },
    "techcrunch": {
        "base_url": "https://techcrunch.com",
        "ai_news_url": "https://techcrunch.com/category/artificial-intelligence/",
        "article_selector": "article.post-block",
        "title_selector": "h2.post-block__title a",
        "use_newspaper": True,
        "category": "ai-startups"
    }
}

def main():
    # Example usage
    scraper = AINewsScraper(db_path="ai_news.db")
    
    # Add configurations manually
    for site_name, config in EXAMPLE_SITE_CONFIGS.items():
        scraper.add_site_config(SiteConfig(
            site_name=site_name,
            base_url=config["base_url"],
            ai_news_url=config["ai_news_url"],
            article_selector=config["article_selector"],
            title_selector=config.get("title_selector"),
            category=config.get("category", "ai-news"),
            use_newspaper=config.get("use_newspaper", True)
        ))
    
    # Or load from a file
    # scraper.load_site_configs("site_configs.json")
    
    # Scrape individual site
    # scraper.scrape_site("venturebeat")
    
    # Scrape all sites
    results = scraper.scrape_all_sites(max_workers=3)
    print(f"Scraping results: {results}")
    
    # Export results
    scraper.export_to_csv("ai_news_export.csv")
    
    # Search for articles
    articles = scraper.search_articles("machine learning")
    for article in articles:
        print(f"{article['title']} - {article['source']} - {article['publish_date']}")

if __name__ == "__main__":
    main()