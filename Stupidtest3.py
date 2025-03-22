import requests
from bs4 import BeautifulSoup
import newspaper
from newspaper import Article
import json
import time
import random
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Callable
import logging
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
    entities: Dict = field(default_factory=dict)
    sentiment: Dict = field(default_factory=dict)
    ai_categories: List = field(default_factory=list)
    article_hash: str = ""
    scrape_date: str = field(default_factory=lambda: datetime.now().isoformat())

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

class JSONBasedScraper:
    """News scraper that stores data in JSON files instead of a database"""
    
    def __init__(self, data_dir: str = "ai_news_data", user_agent: Optional[str] = None):
        self.data_dir = data_dir
        self.site_configs = {}
        self.articles_file = os.path.join(data_dir, "articles.json")
        self.clusters_file = os.path.join(data_dir, "article_clusters.json")
        self.trends_file = os.path.join(data_dir, "trending_topics.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize article storage
        if not os.path.exists(self.articles_file):
            with open(self.articles_file, 'w') as f:
                json.dump([], f)
                
        # Initialize clusters storage
        if not os.path.exists(self.clusters_file):
            with open(self.clusters_file, 'w') as f:
                json.dump([], f)
                
        # Initialize trends storage
        if not os.path.exists(self.trends_file):
            with open(self.trends_file, 'w') as f:
                json.dump({"last_updated": datetime.now().isoformat(), "topics": []}, f)
        
        # Set up a session with rotating user agents
        self.session = requests.Session()
        default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.user_agent = user_agent or default_ua
        self.session.headers.update({"User-Agent": self.user_agent})

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
        """Store an article in the JSON file"""
        try:
            # Load existing articles
            articles = []
            try:
                with open(self.articles_file, 'r') as f:
                    articles = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                articles = []
            
            # Check if article already exists
            article_hashes = [a.get('article_hash') for a in articles]
            if article.article_hash in article_hashes:
                logger.info(f"Article already exists: {article.url}")
                return
            
            # Convert article to dictionary and add to the list
            article_dict = asdict(article)
            articles.append(article_dict)
            
            # Save the updated list
            with open(self.articles_file, 'w') as f:
                json.dump(articles, f, indent=2)
                
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
        """Search for articles in the stored JSON data"""
        try:
            with open(self.articles_file, 'r') as f:
                articles = json.load(f)
            
            # Simple search implementation
            results = []
            for article in articles:
                if (query.lower() in article.get('title', '').lower() or 
                    query.lower() in article.get('text', '').lower() or
                    query.lower() in article.get('summary', '').lower()):
                    # Create a smaller version of the article for results
                    result = {
                        'url': article.get('url'),
                        'title': article.get('title'),
                        'summary': article.get('summary'),
                        'source': article.get('source'),
                        'publish_date': article.get('publish_date'),
                        'category': article.get('category')
                    }
                    results.append(result)
                    
                    if len(results) >= limit:
                        break
            
            return results
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return []

    def export_to_csv(self, output_file: str):
        """Export all articles to a CSV file"""
        try:
            import pandas as pd
            
            with open(self.articles_file, 'r') as f:
                articles = json.load(f)
                
            # Convert to DataFrame
            simplified_articles = []
            for article in articles:
                simplified_articles.append({
                    'url': article.get('url'),
                    'title': article.get('title'),
                    'summary': article.get('summary'),
                    'source': article.get('source'),
                    'publish_date': article.get('publish_date'),
                    'category': article.get('category')
                })
                
            df = pd.DataFrame(simplified_articles)
            df.to_csv(output_file, index=False)
            logger.info(f"Exported {len(df)} articles to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
            
    def get_latest_articles(self, limit: int = 20) -> List[Dict]:
        """Get the most recently scraped articles"""
        try:
            with open(self.articles_file, 'r') as f:
                articles = json.load(f)
                
            # Sort by scrape date (newest first)
            sorted_articles = sorted(articles, 
                                   key=lambda x: x.get('scrape_date', ''), 
                                   reverse=True)
                                   
            # Create simplified versions for output
            results = []
            for article in sorted_articles[:limit]:
                results.append({
                    'url': article.get('url'),
                    'title': article.get('title'),
                    'summary': article.get('summary'),
                    'source': article.get('source'),
                    'publish_date': article.get('publish_date'),
                    'category': article.get('category')
                })
                
            return results
        except Exception as e:
            logger.error(f"Error getting latest articles: {e}")
            return []

# Example configuration
EXAMPLE_SITE_CONFIGS = {
    "techcrunch": {
        "base_url": "https://techcrunch.com",
        "ai_news_url": "https://techcrunch.com/category/artificial-intelligence/",
        "article_selector": "article.post-block",
        "title_selector": "h2.post-block__title a",
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
    "wired": {
        "base_url": "https://www.wired.com",
        "ai_news_url": "https://www.wired.com/tag/artificial-intelligence/",
        "article_selector": "div.SummaryItemWrapper-gdEuvf",
        "title_selector": "h3.SummaryItemHedBase-dZmlME",
        "use_newspaper": True,
        "category": "ai-news"
    }
}

def main():
    """Example usage of the JSON-based scraper"""
    scraper = JSONBasedScraper(data_dir="ai_news_data")
    
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
    
    # You could also load from a config file
    # scraper.load_site_configs("site_configs.json")
    
    # Scrape all sites
    results = scraper.scrape_all_sites(max_workers=3)
    print(f"Scraping results: {results}")
    
    # Show the latest articles
    latest_articles = scraper.get_latest_articles(limit=5)
    print("\nLatest Articles:")
    for article in latest_articles:
        print(f"- {article['title']} ({article['source']})")
        
    # Search for specific topics
    ai_ethics_articles = scraper.search_articles("ethics", limit=3)
    print("\nArticles about AI Ethics:")
    for article in ai_ethics_articles:
        print(f"- {article['title']} ({article['source']})")

if __name__ == "__main__":
    main()