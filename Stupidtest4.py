import newspaper
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download NLTK resources (run once)
# nltk.download('punkt')
# nltk.download('stopwords')

class AINewsScraperFramework:
    """Uniform framework for scraping AI news from multiple websites"""
    
    def __init__(self, websites_list, max_articles_per_site=10):
        """
        Initialize the scraper with a list of website URLs
        
        Args:
            websites_list (list): List of URLs to scrape
            max_articles_per_site (int): Maximum number of articles to extract per site
        """
        self.websites = websites_list
        self.max_articles = max_articles_per_site
        self.results = []
        self.ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning',
            'neural network', 'computer vision', 'nlp', 'natural language processing',
            'llm', 'large language model', 'chatgpt', 'gpt', 'claude', 'gemini',
            'bard', 'ai startup', 'ai company', 'ai investment', 'ai funding',
            'ai research', 'ai model', 'ai ethics', 'ai regulation', 'ai policy'
        ]
        
    def is_ai_related(self, text):
        """Check if content is AI-related based on keywords"""
        text = text.lower()
        for keyword in self.ai_keywords:
            if keyword in text:
                return True
        return False
    
    def extract_with_newspaper(self, url):
        """Extract articles using Newspaper3k"""
        try:
            logger.info(f"Processing site with Newspaper3k: {url}")
            
            # Build site
            site = newspaper.build(url, memoize_articles=False, language='en')
            articles = []
            
            # Limit articles to avoid excessive scraping
            for i, article in enumerate(site.articles):
                if i >= self.max_articles:
                    break
                    
                try:
                    article.download()
                    article.parse()
                    
                    # Skip articles without content
                    if not article.text or len(article.text) < 100:
                        continue
                        
                    # Check if the article is AI-related
                    if self.is_ai_related(article.title + " " + article.text[:2000]):
                        articles.append({
                            'title': article.title,
                            'text': article.text,
                            'url': article.url,
                            'source': url,
                            'date': article.publish_date.strftime('%Y-%m-%d') if article.publish_date else None,
                            'authors': article.authors,
                            'summary': article.summary,
                            'scrape_method': 'newspaper3k'
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing article {article.url}: {str(e)}")
                    
                # Add random delay between article downloads
                time.sleep(random.uniform(1, 3))
                
            return articles
            
        except Exception as e:
            logger.error(f"Error processing site {url} with Newspaper3k: {str(e)}")
            return []
    
    def extract_with_playwright(self, url):
        """Extract content using Playwright for JavaScript-heavy sites"""
        articles = []
        
        try:
            logger.info(f"Processing site with Playwright: {url}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Extract links to articles
                article_links = []
                links = page.query_selector_all('a')
                
                for link in links:
                    href = link.get_attribute('href')
                    if href and ('news' in href or 'blog' in href or 'article' in href):
                        # Ensure we have absolute URLs
                        if href.startswith('/'):
                            href = url.rstrip('/') + href
                        elif not href.startswith('http'):
                            continue
                            
                        article_links.append(href)
                
                # Limit the number of articles
                article_links = list(set(article_links))[:self.max_articles]
                
                # Process each article
                for article_url in article_links:
                    try:
                        article_page = browser.new_page()
                        article_page.goto(article_url, wait_until="networkidle", timeout=60000)
                        
                        title = article_page.title()
                        
                        # Extract main content - adjust selectors as needed
                        content_selectors = [
                            'article', 'main', '.content', '.article-content', 
                            '.post-content', '.entry-content'
                        ]
                        
                        content = ""
                        for selector in content_selectors:
                            content_elem = article_page.query_selector(selector)
                            if content_elem:
                                content = content_elem.inner_text()
                                break
                                
                        if not content:
                            # Fallback to body text
                            body_elem = article_page.query_selector('body')
                            if body_elem:
                                content = body_elem.inner_text()
                            else:
                                content = ""
                        
                        # Check if AI-related
                        if self.is_ai_related(title + " " + content[:2000]):
                            articles.append({
                                'title': title,
                                'text': content,
                                'url': article_url,
                                'source': url,
                                'date': None,  # Date extraction requires site-specific logic
                                'authors': [],
                                'summary': content[:500] + "..." if len(content) > 500 else content,
                                'scrape_method': 'playwright'
                            })
                            
                        article_page.close()
                        
                    except Exception as e:
                        logger.error(f"Error processing article {article_url}: {str(e)}")
                    
                    # Add random delay between article processing
                    time.sleep(random.uniform(2, 5))
                
                browser.close()
                
            return articles
            
        except Exception as e:
            logger.error(f"Error processing site {url} with Playwright: {str(e)}")
            return []
    
    def categorize_content(self, article):
        """
        Categorize content as news, event, startup, or research
        This is a simple rule-based approach - consider using ML classification for better results
        """
        text = (article['title'] + " " + article['text']).lower()
        
        # Check for event indicators
        event_keywords = ['conference', 'event', 'webinar', 'workshop', 'meetup', 'summit']
        for keyword in event_keywords:
            if keyword in text:
                article['category'] = 'event'
                return article
        
        # Check for startup indicators
        startup_keywords = ['startup', 'founded', 'raised', 'funding', 'series a', 
                           'series b', 'venture', 'seed round', 'launch']
        for keyword in startup_keywords:
            if keyword in text:
                article['category'] = 'startup'
                return article
        
        # Check for research indicators
        research_keywords = ['research', 'paper', 'study', 'published', 'findings', 
                            'scientists', 'researchers']
        for keyword in research_keywords:
            if keyword in text:
                article['category'] = 'research'
                return article
        
        # Default to news
        article['category'] = 'news'
        return article
    
    def scrape_site(self, url):
        """Scrape a single site using multiple methods if needed"""
        articles = []
        
        # Try newspaper first
        newspaper_articles = self.extract_with_newspaper(url)
        if newspaper_articles:
            articles.extend(newspaper_articles)
        
        # If newspaper didn't work well, try Playwright
        if len(articles) < 3:
            playwright_articles = self.extract_with_playwright(url)
            articles.extend(playwright_articles)
        
        # Categorize all articles
        articles = [self.categorize_content(article) for article in articles]
        
        return articles
    
    def scrape_all_sites(self, threads=4):
        """Scrape all websites with multi-threading"""
        with ThreadPoolExecutor(max_workers=threads) as executor:
            all_results = list(executor.map(self.scrape_site, self.websites))
        
        # Flatten results
        self.results = [item for sublist in all_results for item in sublist]
        return self.results
    
    def save_results(self, output_file="ai_news_data.json"):
        """Save results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'scrape_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_articles': len(self.results),
                'articles': self.results
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.results)} articles to {output_file}")
        
    def get_results_dataframe(self):
        """Return results as pandas DataFrame"""
        return pd.DataFrame(self.results)

# Example usage
if __name__ == "__main__":
    # Example list of AI news sources
    websites = [
        "https://venturebeat.com/category/ai/",
        "https://www.artificialintelligence-news.com/",
        "https://www.theverge.com/ai-artificial-intelligence",
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://www.wired.com/tag/artificial-intelligence/",
        "https://www.forbes.com/ai-artificial-intelligence/",
        "https://www.technologyreview.com/topic/artificial-intelligence/"
    ]
    
    scraper = AINewsScraperFramework(websites, max_articles_per_site=5)
    results = scraper.scrape_all_sites(threads=3)
    
    # Save to file
    scraper.save_results()
    
    # Display summary
    df = scraper.get_results_dataframe()
    print(f"Total articles scraped: {len(df)}")
    print(f"Articles by category:")
    print(df['category'].value_counts())
    print(f"Articles by source:")
    print(df['source'].value_counts())