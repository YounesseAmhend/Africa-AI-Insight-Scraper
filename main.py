import asyncio
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import aiohttp
import requests
from bs4 import BeautifulSoup
from fastapi import BackgroundTasks, FastAPI, status
from fastapi.responses import JSONResponse

from dtypes.author import Author
from dtypes.source import Source
from utils.custom_driver import CustomDriver
from utils.trigger_file import TriggerFile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# App configuration
app = FastAPI(
    title="Africa-AI-Insight-Scraper",
    description="Web scraper for AI and Africa-related content",
    version="1.0.0"
)

# Constants and configuration
AI_TRIGGER_WORDS_PATH = "./data/ai/trigger_words.txt"
AI_TRIGGER_PHRASES_PATH = "./data/ai/trigger_phrases.txt"
AFRICA_TRIGGER_WORDS_PATH = "./data/africa/trigger_words.txt"
AFRICA_TRIGGER_PHRASES_PATH = "./data/africa/trigger_phrases.txt"

# Rate limiting settings
MIN_DELAY = 1
MAX_DELAY = 3
MAX_WORKERS = 5  # For thread pool

# Load trigger files
try:
    ai_trigger_words = TriggerFile(AI_TRIGGER_WORDS_PATH)
    ai_trigger_phrases = TriggerFile(AI_TRIGGER_PHRASES_PATH)
    africa_trigger_words = TriggerFile(AFRICA_TRIGGER_WORDS_PATH)
    africa_trigger_phrases = TriggerFile(AFRICA_TRIGGER_PHRASES_PATH)

    trigger_words_ai = ai_trigger_words.get()
    trigger_phrases_ai = ai_trigger_phrases.get()
    trigger_words_africa = africa_trigger_words.get()
    trigger_phrases_africa = africa_trigger_phrases.get()
    
    logger.info(f"Loaded {len(trigger_words_ai)} AI trigger words")
    logger.info(f"Loaded {len(trigger_phrases_ai)} AI trigger phrases")
    logger.info(f"Loaded {len(trigger_words_africa)} Africa trigger words")
    logger.info(f"Loaded {len(trigger_phrases_africa)} Africa trigger phrases")
except Exception as e:
    logger.error(f"Error loading trigger files: {str(e)}")
    trigger_words_ai = []
    trigger_phrases_ai = []
    trigger_words_africa = []
    trigger_phrases_africa = []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

sources: List[Source] = [
    {
        "selectors": {
            "next_button": None,
            "title": "header > h3 > a",
            "link": "header > h3 > a",
            "author": {
                "link": ".entry-author > a",
                "name": "strong[itemprop='name']",
            },
            "load_more_button": "a[data-g1-next-page-url]",
        },
        "url": "https://aipressroom.com/events/",
        "trigger_africa": True,
        "trigger_ai": False,
    },
    {
        "selectors": {
            "next_button": None,
            "title": "#event-card-in-search-results > h2",
            "link": "#event-card-in-search-results",
            "author": {
                "link": None,
                "name": '[data-event-label="hosted-by"] div:nth-of-type(2) > div:last-child',
            },
            "load_more_button": None,
        },
        "url": "https://www.meetup.com/find/",
        "trigger_africa": True,
        "trigger_ai": True,
    },
    {
        "url": "https://um6p.ma/actualites",
        "selectors": {
            "next_button": ".pager__item--next > a",
            "title": ".post-title > a",
            "link": ".post-title > a",
            "author": None,
            "load_more_button": None,
        },
        "trigger_africa": False,
        "trigger_ai": True,
    },
    {
        "url": "https://www.up.ac.za/news",
        "selectors": {
            "next_button": "li.next > a",
            "title": "ul.news-list > li > a",
            "link": "ul.news-list > li > a",
            "author": None,
            "load_more_button": None,
        },
        "trigger_africa": False,
        "trigger_ai": True,
    },
]

# Utility functions
def normalize_url(url: Any, base_url: str) -> str:
    """Normalize URL to absolute form if it's relative"""
    if not url:
        return ""
    
    url_str = str(url)
    if url_str.startswith('/'):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}://{parsed_base.netloc}{url_str}"
    elif not url_str.startswith(('http://', 'https://')):
        parsed_base = urlparse(base_url)
        return f"{parsed_base.scheme}://{parsed_base.netloc}/{url_str}"
    return url_str

def contains_triggers(text: str, trigger_words: List[str], trigger_phrases: List[str]) -> bool:
    """Check if text contains any trigger words or phrases"""
    if not text:
        return False
        
    text_lower = text.lower()
    words = set(word.lower() for word in text.split())
    
    # Check for trigger words
    for word in trigger_words:
        if word.lower() in words:
            logger.debug(f"Found trigger word: {word} in '{text}'")
            return True
            
    # Check for trigger phrases
    for phrase in trigger_phrases:
        if phrase.lower() in text_lower:
            logger.debug(f"Found trigger phrase: {phrase} in '{text}'")
            return True
            
    return False

def should_include_content(title: str, trigger_ai: bool, trigger_africa: bool) -> bool:
    """Determine if content should be included based on trigger settings"""
    if not title:
        return False
        
    # Check for AI triggers if required
    should_add_ai = False
    if trigger_ai:
        should_add_ai = contains_triggers(title, trigger_words_ai, trigger_phrases_ai)
        
    # Check for Africa triggers if required
    should_add_africa = False
    if trigger_africa:
        should_add_africa = contains_triggers(title, trigger_words_africa, trigger_phrases_africa)
    
    # Logical check based on trigger requirements
    # If trigger_ai is True, we require AI triggers
    # If trigger_africa is True, we require Africa triggers
    result = (not trigger_ai or should_add_ai) and (not trigger_africa or should_add_africa)
    
    if result:
        logger.debug(f"Including content: '{title}' (AI: {should_add_ai}, Africa: {should_add_africa})")
    
    return result

async def fetch_author_info_async(session: aiohttp.ClientSession, link: str, author_selector: Any) -> Optional[Author]:
    """Fetch author information asynchronously"""
    if not author_selector:
        return None
        
    try:
        async with session.get(link, headers=HEADERS) as response:
            if response.status != 200:
                logger.warning(f"Failed to fetch author info from {link}: HTTP {response.status}")
                return None
                
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            
            name_selector = author_selector.get("name")
            link_selector = author_selector.get("link")
            
            author_name_element = soup.select_one(str(name_selector)) if name_selector else None
            author_link_element = soup.select_one(str(link_selector)) if link_selector else None
            
            author_name = author_name_element.get_text().strip() if author_name_element else "Unknown"
            author_link = None
            
            if author_link_element and hasattr(author_link_element, "get"):
                href = author_link_element.get("href")
                if href:
                    author_link = normalize_url(href, link)
            
            return {
                "name": author_name,
                "link": author_link
            }
    except Exception as e:
        logger.error(f"Error fetching author info from {link}: {str(e)}")
        return None

def fetch_author_info(link: str, author_selector: Any) -> Optional[Author]:
    """Fetch author information synchronously"""
    if not author_selector:
        return None
        
    try:
        # Add random delay for rate limiting
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        
        response = requests.get(url=link, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch author info from {link}: HTTP {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        name_selector = author_selector.get("name")
        link_selector = author_selector.get("link")
        
        author_name_element = soup.select_one(str(name_selector)) if name_selector else None
        author_link_element = soup.select_one(str(link_selector)) if link_selector else None
        
        author_name = author_name_element.get_text().strip() if author_name_element else "Unknown"
        author_link = None
        
        if author_link_element and hasattr(author_link_element, "get"):
            href = author_link_element.get("href")
            if href:
                author_link = normalize_url(href, link)
        
        return {
            "name": author_name,
            "link": author_link
        }
    except Exception as e:
        logger.error(f"Error fetching author info from {link}: {str(e)}")
        return None

# Scraping functions
async def scrape_source_async(source: Source) -> List[Dict]:
    """Scrape a single source asynchronously"""
    source_results = []
    url = source["url"]
    
    try:
        logger.info(f"Processing source: {url}")
        
        # Extract source configuration
        trigger_ai = source["trigger_ai"]
        trigger_africa = source["trigger_africa"]
        selector = source["selectors"]
        author_selector = selector["author"]
        next_button_selector = selector['next_button']
        load_more_selector = selector["load_more_button"]
        
        # Get HTML using CustomDriver
        logger.info(f"Navigating to URL: {url}")
        html = ""
        
        try:
            CustomDriver.get(url)
            
            if next_button_selector is None:
                logger.debug(f"No pagination found. Using scroll to end with load_more_selector: {load_more_selector}")
                CustomDriver.scroll_to_end(load_more_selector, timeout_s=10)
                html = CustomDriver.get_html()
            else:
                logger.debug(f"Pagination found. Using next button selector: {next_button_selector}")
                html = CustomDriver.handle_pagination(next_button_selector, timeout_s=10)
        except Exception as e:
            logger.error(f"Error navigating page {url}: {str(e)}")
            return source_results
            
        # Parse HTML
        try:
            soup = BeautifulSoup(html, "html.parser")
            elements = soup.select(selector["title"])
            links = soup.select(selector["link"])
            
            logger.info(f"Found {len(elements)} title elements and {len(links)} link elements")
            
            # Collect articles that match criteria
            article_data = []
            
            for i, element in enumerate(elements):
                if i >= len(links):
                    logger.warning(f"Mismatch between elements and links at index {i}")
                    continue
                    
                title = element.get_text().strip()
                link_element = links[i]
                link = ""
                
                if hasattr(link_element, "get"):
                    href = link_element.get("href")
                    if href:
                        link = normalize_url(href, url)
                
                if not link:
                    logger.debug(f"Skipping article with empty link: {title}")
                    continue
                
                # Check if the article matches our criteria
                if should_include_content(title, trigger_ai, trigger_africa):
                    logger.debug(f"Adding article: {title}")
                    article_data.append({
                        "title": title,
                        "link": link,
                        "author_selector": author_selector
                    })
            
            # Fetch author information asynchronously
            if article_data:
                logger.info(f"Fetching author information for {len(article_data)} articles")
                
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for article in article_data:
                        tasks.append(
                            fetch_author_info_async(
                                session, 
                                article["link"], 
                                article["author_selector"]
                            ) if article["author_selector"] else None
                        )
                    
                    # Process in batches to avoid rate limiting
                    batch_size = 5
                    for i in range(0, len(tasks), batch_size):
                        batch = tasks[i:i+batch_size]
                        # Only gather non-None tasks
                        valid_batch = [task for task in batch if task is not None]
                        
                        if valid_batch:
                            authors = await asyncio.gather(*valid_batch)
                            
                            # Match authors with articles
                            author_index = 0
                            for j in range(i, min(i+batch_size, len(article_data))):
                                if article_data[j]["author_selector"]:
                                    if author_index < len(authors):
                                        article = {
                                            "title": article_data[j]["title"],
                                            "link": article_data[j]["link"],
                                            "author": authors[author_index]
                                        }
                                        author_index += 1
                                    else:
                                        article = {
                                            "title": article_data[j]["title"],
                                            "link": article_data[j]["link"],
                                            "author": None
                                        }
                                else:
                                    article = {
                                        "title": article_data[j]["title"],
                                        "link": article_data[j]["link"],
                                        "author": None
                                    }
                                
                                source_results.append(article)
                        else:
                            # No author info to fetch for this batch
                            for j in range(i, min(i+batch_size, len(article_data))):
                                article = {
                                    "title": article_data[j]["title"],
                                    "link": article_data[j]["link"],
                                    "author": None
                                }
                                source_results.append(article)
                            
                        # Add delay between batches
                        if i + batch_size < len(tasks):
                            await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        except Exception as e:
            logger.error(f"Error processing HTML from {url}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error scraping source {url}: {str(e)}")
    
    logger.info(f"Found {len(source_results)} results from {url}")
    return source_results

def scrape_source(source: Source) -> List[Dict]:
    """Scrape a single source synchronously"""
    source_results = []
    url = source["url"]
    
    try:
        logger.info(f"Processing source: {url}")
        
        # Extract source configuration
        trigger_ai = source["trigger_ai"]
        trigger_africa = source["trigger_africa"]
        selector = source["selectors"]
        author_selector = selector["author"]
        next_button_selector = selector['next_button']
        load_more_selector = selector["load_more_button"]
        
        # Get HTML using CustomDriver
        logger.info(f"Navigating to URL: {url}")
        html = ""
        
        try:
            CustomDriver.get(url)
            
            if next_button_selector is None:
                logger.debug(f"No pagination found. Using scroll to end with load_more_selector: {load_more_selector}")
                CustomDriver.scroll_to_end(load_more_selector, timeout_s=10)
                html = CustomDriver.get_html()
            else:
                logger.debug(f"Pagination found. Using next button selector: {next_button_selector}")
                html = CustomDriver.handle_pagination(next_button_selector, timeout_s=10)
        except Exception as e:
            logger.error(f"Error navigating page {url}: {str(e)}")
            return source_results
            
        # Parse HTML
        try:
            soup = BeautifulSoup(html, "html.parser")
            elements = soup.select(selector["title"])
            links = soup.select(selector["link"])
            
            logger.info(f"Found {len(elements)} title elements and {len(links)} link elements")
            
            # Collect and process articles
            article_links = []
            
            for i, element in enumerate(elements):
                if i >= len(links):
                    logger.warning(f"Mismatch between elements and links at index {i}")
                    continue
                    
                title = element.get_text().strip()
                link_element = links[i]
                link = ""
                
                if hasattr(link_element, "get"):
                    href = link_element.get("href")
                    if href:
                        link = normalize_url(href, url)
                
                if not link:
                    logger.debug(f"Skipping article with empty link: {title}")
                    continue
                
                # Check if the article matches our criteria
                if should_include_content(title, trigger_ai, trigger_africa):
                    logger.debug(f"Adding article: {title}")
                    article_links.append({
                        "title": title,
                        "link": link
                    })
            
            # Fetch author information with thread pool
            if article_links and author_selector:
                logger.info(f"Fetching author information for {len(article_links)} articles")
                
                # Process in batches with ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = []
                    for article in article_links:
                        futures.append(
                            executor.submit(
                                fetch_author_info, 
                                article["link"], 
                                author_selector
                            )
                        )
                    
                    # Process results as they complete
                    for i, future in enumerate(futures):
                        author = future.result()
                        source_results.append({
                            "title": article_links[i]["title"],
                            "link": article_links[i]["link"],
                            "author": author
                        })
            else:
                # No author information needed
                for article in article_links:
                    source_results.append({
                        "title": article["title"],
                        "link": article["link"],
                        "author": None
                    })
                
        except Exception as e:
            logger.error(f"Error processing HTML from {url}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error scraping source {url}: {str(e)}")
    
    logger.info(f"Found {len(source_results)} results from {url}")
    return source_results

async def scrape_all_sources_async() -> List[Dict]:
    """Scrape all sources asynchronously"""
    tasks = [scrape_source_async(source) for source in sources]
    results = await asyncio.gather(*tasks)
    
    all_results = []
    for result in results:
        all_results.extend(result)
    
    logger.info(f"Total results found: {len(all_results)}")
    return all_results

def scrape_all_sources() -> List[Dict]:
    """Scrape all sources using thread pool"""
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(scrape_source, sources))
    
    all_results = []
    for result in results:
        all_results.extend(result)
    
    logger.info(f"Total results found: {len(all_results)}")
    return all_results

# Background task function
def background_scrape_task():
    """Function for background scraping task"""
    try:
        logger.info("Starting background scraping task")
        results = scrape_all_sources()
        logger.info(f"Background task completed with {len(results)} results")
        # Here you could save results to a database or file if needed
    except Exception as e:
        logger.error(f"Error in background scraping task: {str(e)}")

# API Endpoints
@app.get("/scrape", status_code=status.HTTP_200_OK)
def scrape_endpoint():
    """Synchronous endpoint to scrape sources"""
    try:
        logger.info("Starting synchronous scraping")
        all_results = scrape_all_sources()
        return all_results
    except Exception as e:
        logger.error(f"Error in synchronous scraping: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

@app.get("/scrape-async", status_code=status.HTTP_200_OK)
async def scrape_async_endpoint():
    """Asynchronous endpoint to scrape sources"""
    try:
        logger.info("Starting asynchronous scraping")
        all_results = await scrape_all_sources_async()
        return all_results
    except Exception as e:
        logger.error(f"Error in asynchronous scraping: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

@app.post("/background-scrape", status_code=status.HTTP_202_ACCEPTED)
def background_scrape_endpoint(background_tasks: BackgroundTasks):
    """Start a background task to scrape sources"""
    try:
        background_tasks.add_task(background_scrape_task)
        logger.info("Background scraping task started")
        return {"message": "Scraping started in the background"}
    except Exception as e:
        logger.error(f"Error starting background task: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": str(e)}
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Enhanced health check endpoint"""
    return {
        "status": "ok",
        "version": app.version,
        "sources": len(sources),
        "trigger_words": {
            "ai": len(trigger_words_ai),
            "africa": len(trigger_words_africa)
        }
    }

# Keep the original scrape-batch endpoint for backward compatibility
@app.get("/scrape-batch")
def root_legacy():
    """Legacy endpoint for backward compatibility"""
    logger.warning("Using deprecated /scrape-batch endpoint. Please migrate to /scrape.")
    return scrape_endpoint()