"""
Africa AI News & Startup Scraper
- Uses Scrapy as the main framework
- Integrates Newspaper3k for article parsing
- Falls back to Selenium for JavaScript-rendered sites
- Implements dynamic selector learning for adaptable scraping
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
import json
import re
import time
from datetime import datetime
from urllib.parse import urlparse
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter, defaultdict
from bs4 import BeautifulSoup

class DynamicSelectorLearner:
    """
    Class for dynamically learning and generating selectors based on page structure analysis
    """
    
    def __init__(self):
        self.selector_patterns = defaultdict(list)
        self.learned_selectors = {}
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 6))
        
    def analyze_page(self, html, page_type):
        """Analyze page structure and learn common patterns for specified content type"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract common elements based on content type
        if page_type == 'news':
            self._analyze_news_elements(soup)
        elif page_type == 'startup':
            self._analyze_startup_elements(soup)
        elif page_type == 'event':
            self._analyze_event_elements(soup)
            
        # Update learned selectors after sufficient samples
        if len(self.selector_patterns[page_type]) >= 5:
            self._generate_learned_selectors(page_type)
                
    def _analyze_news_elements(self, soup):
        """Analyze news article elements and store their attributes and patterns"""
        patterns = {}
        
        # Find potential title elements (h1, h2 elements with specific classes)
        title_candidates = soup.find_all(['h1', 'h2', 'header'])
        if title_candidates:
            patterns['title'] = self._extract_element_patterns(title_candidates)
            
        # Find potential content elements (article, div with many paragraphs)
        content_candidates = soup.find_all('article') + [div for div in soup.find_all('div') if len(div.find_all('p')) > 3]
        if content_candidates:
            patterns['content'] = self._extract_element_patterns(content_candidates)
            
        # Find potential date elements
        date_candidates = soup.find_all(['time', 'span', 'div'], class_=lambda c: c and ('date' in c.lower() or 'time' in c.lower()))
        if date_candidates:
            patterns['date'] = self._extract_element_patterns(date_candidates)
            
        # Find potential author elements
        author_candidates = soup.find_all(['span', 'a', 'div'], class_=lambda c: c and ('author' in c.lower() or 'byline' in c.lower()))
        if author_candidates:
            patterns['author'] = self._extract_element_patterns(author_candidates)
            
        self.selector_patterns['news'].append(patterns)
        
    def _analyze_startup_elements(self, soup):
        """Analyze startup profile elements and store their attributes and patterns"""
        patterns = {}
        
        # Find potential name elements
        name_candidates = soup.find_all(['h1', 'h2', 'div'], class_=lambda c: c and ('name' in c.lower() or 'title' in c.lower()))
        if name_candidates:
            patterns['name'] = self._extract_element_patterns(name_candidates)
            
        # Find potential description elements
        desc_candidates = soup.find_all(['div', 'p'], class_=lambda c: c and ('description' in c.lower() or 'about' in c.lower()))
        if desc_candidates:
            patterns['description'] = self._extract_element_patterns(desc_candidates)
            
        # Find potential location elements
        location_candidates = soup.find_all(['div', 'span'], class_=lambda c: c and ('location' in c.lower() or 'address' in c.lower()))
        if location_candidates:
            patterns['location'] = self._extract_element_patterns(location_candidates)
            
        self.selector_patterns['startup'].append(patterns)
        
    def _analyze_event_elements(self, soup):
        """Analyze event listing elements and store their attributes and patterns"""
        patterns = {}
        
        # Find potential event title elements
        title_candidates = soup.find_all(['h1', 'h2', 'h3'], class_=lambda c: c and ('title' in c.lower() or 'name' in c.lower()))
        if title_candidates:
            patterns['title'] = self._extract_element_patterns(title_candidates)
            
        # Find potential event date elements
        date_candidates = soup.find_all(['time', 'div', 'span'], class_=lambda c: c and ('date' in c.lower() or 'when' in c.lower()))
        if date_candidates:
            patterns['date'] = self._extract_element_patterns(date_candidates)
            
        # Find potential location elements
        location_candidates = soup.find_all(['div', 'span', 'p'], class_=lambda c: c and ('location' in c.lower() or 'venue' in c.lower() or 'where' in c.lower()))
        if location_candidates:
            patterns['location'] = self._extract_element_patterns(location_candidates)
            
        self.selector_patterns['event'].append(patterns)
        
    def _extract_element_patterns(self, elements):
        """Extract patterns from elements such as tag types, class names, and attributes"""
        patterns = {
            'tags': Counter(),
            'classes': Counter(),
            'attributes': Counter(),
            'parent_classes': Counter(),
            'path_fragments': Counter()
        }
        
        for element in elements:
            # Basic element properties
            patterns['tags'][element.name] += 1
            
            # Classes
            if element.get('class'):
                for cls in element.get('class'):
                    patterns['classes'][cls] += 1
            
            # Other attributes
            for attr in element.attrs:
                if attr != 'class':
                    patterns['attributes'][attr] += 1
            
            # Parent classes
            if element.parent and element.parent.get('class'):
                for cls in element.parent.get('class'):
                    patterns['parent_classes'][cls] += 1
            
            # Path fragments - get CSS path components
            path_parts = []
            parent = element
            for _ in range(3):  # Only go up a few levels
                if parent:
                    if parent.name:
                        part = parent.name
                        if parent.get('class'):
                            part += '.' + '.'.join(parent.get('class'))
                        path_parts.append(part)
                    parent = parent.parent
            
            if path_parts:
                path = ' > '.join(reversed(path_parts))
                patterns['path_fragments'][path] += 1
        
        return patterns
    
    def _generate_learned_selectors(self, page_type):
        """Generate optimized selectors from collected patterns using clustering"""
        if not self.selector_patterns[page_type]:
            return
            
        selectors = {}
        
        # For each element type (title, content, etc.)
        element_types = set()
        for pattern in self.selector_patterns[page_type]:
            element_types.update(pattern.keys())
            
        for element_type in element_types:
            # Collect all patterns for this element type
            all_patterns = []
            for pattern in self.selector_patterns[page_type]:
                if element_type in pattern:
                    all_patterns.append(pattern[element_type])
            
            if not all_patterns:
                continue
                
            # Generate CSS selectors based on most common patterns
            tag_selectors = []
            class_selectors = []
            composite_selectors = []
            
            # Process tags
            all_tags = Counter()
            for pattern in all_patterns:
                all_tags.update(pattern['tags'])
            
            common_tags = [tag for tag, count in all_tags.most_common(3) if count >= 2]
            
            # Process classes
            all_classes = Counter()
            for pattern in all_patterns:
                all_classes.update(pattern['classes'])
            
            common_classes = [cls for cls, count in all_classes.most_common(5) if count >= 2]
            
            # Create selectors
            for tag in common_tags:
                tag_selectors.append(f"{tag}")
                
                for cls in common_classes:
                    composite_selectors.append(f"{tag}.{cls}")
            
            for cls in common_classes:
                class_selectors.append(f".{cls}")
            
            # Get most promising path fragments
            all_paths = Counter()
            for pattern in all_patterns:
                all_paths.update(pattern['path_fragments'])
            
            path_selectors = [path for path, count in all_paths.most_common(3) if count >= 2]
            
            # Combine all selectors, prioritizing composite ones
            all_selectors = composite_selectors + class_selectors + tag_selectors + path_selectors
            
            # Store learned selectors
            selectors[element_type] = all_selectors[:5]  # Keep top 5 most promising selectors
        
        self.learned_selectors[page_type] = selectors
    
    def get_selectors(self, element_type, page_type):
        """Get learned selectors for a specific element type and page type"""
        if page_type in self.learned_selectors and element_type in self.learned_selectors[page_type]:
            return self.learned_selectors[page_type][element_type]
        
        # Fallback to default selectors if we haven't learned any yet
        return self._get_default_selectors(element_type, page_type)
    
    def _get_default_selectors(self, element_type, page_type):
        """Provide sensible default selectors based on common web patterns"""
        defaults = {
            'news': {
                'title': ['h1', '.title', '.article-title', '.headline', 'article h1'],
                'content': ['article', '.content', '.article-content', '.entry-content', 'main'],
                'date': ['.date', 'time', '.published', '.article-date', '.timestamp'],
                'author': ['.author', '.byline', '.article-author', '.meta-author']
            },
            'startup': {
                'name': ['h1', '.company-name', '.startup-name', '.title'],
                'description': ['.description', '.about', '.company-description', 'p.summary'],
                'location': ['.location', '.address', '.headquarters', '.company-location']
            },
            'event': {
                'title': ['h1', '.event-title', '.event-name', '.title'],
                'date': ['.date', '.event-date', 'time', '.when'],
                'location': ['.location', '.venue', '.where', '.event-location']
            }
        }
        
        if page_type in defaults and element_type in defaults[page_type]:
            return defaults[page_type][element_type]
        return []

class AfricaAISpider(scrapy.Spider):
    name = "africa_ai_spider"
    
    # Define your list of websites to scrape
    start_urls = [
        # News sites
        "https://www.up.ac.za/news",
        "https://um6p.ma/actualites",
        "https://afrique.le360.ma/politique/",
        "https://www.digitalbusiness.africa/le-tchad-aura-besoin-de-1-452-milliards-de-francs-cfa-pour-financer-son-plan-strategique-de-developpement-du-numerique-2020-2030-valide/"
        # Add more URLs as needed
    ]
    
    # Define common AI-related keywords for content filtering
    ai_keywords = [
        "artificial intelligence", "ai ", "machine learning", "ml ", "deep learning",
        "neural network", "nlp", "natural language processing", "computer vision",
        "data science", "robotics", "automation", "startup", "innovation", 
        "tech hub", "incubator", "accelerator", "funding", "investment"
    ]
    
    # Country keywords to identify African focus
    african_countries = [
        "algeria", "angola", "benin", "botswana", "burkina faso", "burundi", 
        "cabo verde", "cameroon", "central african republic", "chad", "comoros",
        "congo", "djibouti", "egypt", "equatorial guinea", "eritrea", "ethiopia",
        "gabon", "gambia", "ghana", "guinea", "guinea-bissau", "ivory coast",
        "côte d'ivoire", "kenya", "lesotho", "liberia", "libya", "madagascar",
        "malawi", "mali", "mauritania", "mauritius", "morocco", "mozambique", 
        "namibia", "niger", "nigeria", "rwanda", "são tomé and príncipe", 
        "senegal", "seychelles", "sierra leone", "somalia", "south africa", 
        "south sudan", "sudan", "swaziland", "eswatini", "tanzania", "togo", 
        "tunisia", "uganda", "zambia", "zimbabwe", "africa", "african"
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'CONCURRENT_REQUESTS': 5,  # Be respectful with rate limiting
        'DOWNLOAD_DELAY': 2,  # 2 second delay between requests to the same site
        'ROBOTSTXT_OBEY': True,
        'ITEM_PIPELINES': {
            '__main__.JsonExportPipeline': 300,
        },
        'LOG_LEVEL': 'INFO',
    }
    
    def __init__(self, *args, **kwargs):
        super(AfricaAISpider, self).__init__(*args, **kwargs)
        # Setup Selenium for JavaScript-rendered sites
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.service = Service(ChromeDriverManager().install())
        self.driver = None  # Initialize only when needed
        
        # Initialize the dynamic selector learner
        self.selector_learner = DynamicSelectorLearner()
        
        # Track websites we've seen for learning purposes
        self.processed_domains = set()
        
    def parse(self, response):
        """Main parsing function to handle different website structures"""
        hostname = urlparse(response.url).netloc
        
        # Detect page type 
        page_type = self._detect_page_type(response)
        
        # Feed the page to our selector learner
        self.selector_learner.analyze_page(response.text, page_type)
        
        # Add to processed domains
        self.processed_domains.add(hostname)
        
        # Use learned or default selectors to extract content based on page type
        if page_type == 'news':
            yield from self._parse_news_with_learned_selectors(response)
        elif page_type == 'startup':
            yield from self._parse_startup_with_learned_selectors(response)
        elif page_type == 'event':
            yield from self._parse_event_with_learned_selectors(response)
        else:
            # Generic approach for other sites
            yield from self._parse_generic_page(response)
        
        # Follow pagination if available
        pagination = self._extract_pagination(response)
        if pagination:
            yield scrapy.Request(url=pagination, callback=self.parse)
    
    def _detect_page_type(self, response):
        """Detect page type based on URL and content analysis"""
        url = response.url
        text = ' '.join(response.css('body ::text').getall())
        
        # Check URL patterns
        if any(kw in url.lower() for kw in ['news', 'article', 'blog', 'actualites']):
            return 'news'
        elif any(kw in url.lower() for kw in ['startup', 'company', 'venture', 'business']):
            return 'startup'
        elif any(kw in url.lower() for kw in ['event', 'conference', 'meetup', 'workshop']):
            return 'event'
            
        # Check content patterns
        if any(kw in text.lower() for kw in ['article', 'published on', 'posted on']):
            return 'news'
        elif any(kw in text.lower() for kw in ['founded', 'company profile', 'about us']):
            return 'startup'
        elif any(kw in text.lower() for kw in ['register now', 'schedule', 'speakers']):
            return 'event'
            
        # Default to news as most common type
        return 'news'
    
    def _parse_news_with_learned_selectors(self, response):
        """Parse news site using dynamically learned selectors"""
        # Get selectors for article links
        article_url_selectors = [
            'a[href*=article]', 'a[href*=news]', 'a[href*=story]', 
            '.headline a', '.news-item a', '.post a', 'article a',
            '.entry a', '.post-title a'
        ]
        
        # Try to find article links
        article_links = []
        for selector in article_url_selectors:
            links = response.css(selector)
            if links:
                article_links.extend(links)
                
        # If we have article links, follow them
        if article_links:
            for link in article_links[:10]:  # Limit to first 10 articles
                article_url = link.css('::attr(href)').get()
                if not article_url:
                    continue
                    
                article_url = response.urljoin(article_url)
                
                # Quick check if the URL seems relevant
                if self._url_seems_relevant(article_url):
                    yield scrapy.Request(
                        url=article_url,
                        callback=self._parse_article_with_selectors,
                        meta={'type': 'news'}
                    )
            return
            
        # If no article links found, check if current page is an article
        title_selectors = self.selector_learner.get_selectors('title', 'news')
        content_selectors = self.selector_learner.get_selectors('content', 'news')
        
        # Try to extract title using learned selectors
        title = None
        for selector in title_selectors:
            title = response.css(f"{selector}::text").get()
            if title:
                break
                
        # Try to extract content using learned selectors
        content = None
        for selector in content_selectors:
            paragraphs = response.css(f"{selector} p::text").getall()
            if paragraphs:
                content = ' '.join(paragraphs)
                break
                
        # If we found title and content, process as article
        if title and content and self._content_is_relevant(f"{title} {content}"):
            item = self._extract_article_from_response(response)
            if item:
                yield item
    
    def _parse_article_with_selectors(self, response):
        """Extract article using dynamically learned selectors first, then fallback to newspaper3k"""
        # Try with learned selectors first
        title_selectors = self.selector_learner.get_selectors('title', 'news')
        content_selectors = self.selector_learner.get_selectors('content', 'news')
        date_selectors = self.selector_learner.get_selectors('date', 'news')
        author_selectors = self.selector_learner.get_selectors('author', 'news')
        
        # Extract title
        title = None
        for selector in title_selectors:
            title = response.css(f"{selector}::text").get()
            if not title:
                title = response.css(selector).get()
            if title:
                title = title.strip()
                break
                
        # Extract content
        content = None
        for selector in content_selectors:
            paragraphs = response.css(f"{selector} p::text").getall()
            if paragraphs:
                content = ' '.join(paragraphs).strip()
                break
                
        # Extract date
        publish_date = None
        for selector in date_selectors:
            date_text = response.css(f"{selector}::text").get()
            if not date_text:
                date_text = response.css(f"{selector}::attr(datetime)").get()
            if date_text:
                publish_date = date_text.strip()
                break
                
        # Extract author
        author = None
        for selector in author_selectors:
            author_text = response.css(f"{selector}::text").get()
            if author_text:
                author = author_text.strip()
                break
                
        # If we got good data with selectors, use it
        if title and content and self._content_is_relevant(f"{title} {content}"):
            item = {
                'title': title,
                'url': response.url,
                'text': content,
                'source': urlparse(response.url).netloc,
                'type': 'news',
                'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'extraction_method': 'dynamic_selectors'
            }
            
            if publish_date:
                item['publish_date'] = publish_date
                
            if author:
                item['authors'] = [author]
                
            return item
                
        # Fallback to newspaper3k for extraction
        return self._parse_article_content(response)
        
    def _parse_startup_with_learned_selectors(self, response):
        """Parse startup directory using dynamically learned selectors"""
        # Get selectors for startup profile links
        profile_selectors = [
            'a[href*=startup]', 'a[href*=company]', 'a[href*=venture]',
            '.startup-card a', '.company-item a', '.venture-listing a'
        ]
        
        # Try to find startup profile links
        profile_links = []
        for selector in profile_selectors:
            links = response.css(selector)
            if links:
                profile_links.extend(links)
                
        # If we have profile links, follow them
        if profile_links:
            for link in profile_links[:10]:  # Limit to first 10 profiles
                profile_url = link.css('::attr(href)').get()
                if not profile_url:
                    continue
                    
                profile_url = response.urljoin(profile_url)
                
                yield scrapy.Request(
                    url=profile_url,
                    callback=self._parse_startup_profile_with_selectors,
                    meta={'type': 'startup'}
                )
            return
            
        # If no profile links found, check if current page is a profile
        item = self._parse_startup_profile_with_selectors(response)
        if item:
            yield item
    
    def _parse_startup_profile_with_selectors(self, response):
        """Extract startup profile using dynamically learned selectors"""
        # Get learned selectors
        name_selectors = self.selector_learner.get_selectors('name', 'startup')
        desc_selectors = self.selector_learner.get_selectors('description', 'startup')
        location_selectors = self.selector_learner.get_selectors('location', 'startup')
        
        # Extract name
        name = None
        for selector in name_selectors:
            name = response.css(f"{selector}::text").get()
            if not name:
                name = response.css(selector).get()
            if name:
                name = name.strip()
                break
                
        # Extract description
        description = None
        for selector in desc_selectors:
            desc_text = response.css(f"{selector}::text").get()
            if not desc_text:
                desc_paragraphs = response.css(f"{selector} p::text").getall()
                if desc_paragraphs:
                    desc_text = ' '.join(desc_paragraphs)
            if desc_text:
                description = desc_text.strip()
                break
                
        # Extract location
        location = None
        for selector in location_selectors:
            loc_text = response.css(f"{selector}::text").get()
            if loc_text:
                location = loc_text.strip()
                break
                
        # If we have enough data and it's relevant, create item
        if name and description and self._content_is_relevant(f"{name} {description}"):
            item = {
                'name': name,
                'url': response.url,
                'description': description,
                'source': urlparse(response.url).netloc,
                'type': 'startup',
                'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'extraction_method': 'dynamic_selectors'
            }
            
            if location:
                item['location'] = location
                
            # Try to extract other details
            other_details = self._extract_startup_details_dynamic(response)
            item.update(other_details)
            
            return item
            
        # If dynamic extraction failed, fallback to traditional methods
        return self._parse_startup_profile(response)
    
    def _extract_startup_details_dynamic(self, response):
        """Dynamically extract additional startup details"""
        details = {}
        
        # Look for funding info
        funding_patterns = [
            '.funding', '.investment', '.raised', 
            'text:contains("funding")', 'text:contains("raised")'
        ]
        
        for pattern in funding_patterns:
            funding_text = None
            if 'text:contains' in pattern:
                search_term = pattern.split('(')[1].split(')')[0].replace('"', '')
                elements = response.xpath(f"//*[contains(text(), '{search_term}')]")
                if elements:
                    funding_text = elements[0].get()
            else:
                funding_text = response.css(f"{pattern}::text").get()
                
            if funding_text:
                details['funding'] = funding_text.strip()
                break
                
        # Look for founding year
        year_patterns = [
            '.founded', '.year', '.established',
            'text:contains("founded")', 'text:contains("established in")'
        ]
        
        for pattern in year_patterns:
            year_text = None
            if 'text:contains' in pattern:
                search_term = pattern.split('(')[1].split(')')[0].replace('"', '')
                elements = response.xpath(f"//*[contains(text(), '{search_term}')]")
                if elements:
                    year_text = elements[0].get()
            else:
                year_text = response.css(f"{pattern}::text").get()
                
            if year_text:
                # Extract year using regex
                year_match = re.search(r'20\d\d|19\d\d', year_text)
                if year_match:
                    details['founding_year'] = year_match.group(0)
                else:
                    details['founding_year'] = year_text.strip()
                break
                
        return details
    
    def _parse_event_with_learned_selectors(self, response):
        """Parse event listings using dynamically learned selectors"""
        # Get selectors for event links
        event_selectors = [
            'a[href*=event]', 'a[href*=conference]', 
            '.event-card a', '.event-listing a', '.conf-item a'
        ]
        
        # Try to find event links
        event_links = []
        for selector in event_selectors:
            links = response.css(selector)
            if links:
                event_links.extend(links)
                
        # If we have event links, follow them
        if event_links:
            for link in event_links[:10]:  # Limit to first 10 events
                event_url = link.css('::attr(href)').get()
                if not event_url:
                    continue
                    
                event_url = response.urljoin(event_url)
                
                yield scrapy.Request(
                    url=event_url,
                    callback=self._parse_event_details_with_selectors,
                    meta={'type': 'event'}
                )
            return
            
        # If no event links found, check if current page is an event
        item = self._parse_event_details_with_selectors(response)
        if item:
            yield item
        
    def _parse_event_details_with_selectors(self, response):
        """Extract event details using dynamically learned selectors"""
        # Get learned selectors
        title_selectors = self.selector_learner.get_selectors('title', 'event')
        date_selectors = self.selector_learner.get_selectors('date', 'event')
        location_selectors = self.selector_learner.get_selectors('location', 'event')
        
        # Add some generic description selectors
        desc_selectors = ['.description', '.about', '.event-description', 'section p', 'main p']
        
        # Extract title
        title = None
        for selector in title_selectors:
            title = response.css(f"{selector}::text").get()
            if not title:
                title = response.css(selector).get()
            if title:
                title = title.strip()
                break
                
        # Extract description
        description = None
        for selector in desc_selectors:
            desc_text = response.css(f"{selector}::text").get()
            if not desc_text:
                desc_paragraphs = response.css(f"{selector} p::text").getall()
                if desc_paragraphs:
                    desc_text = ' '.join(desc_paragraphs)
            if desc_text:
                description = desc_text.strip()
                break
                
        # Extract date
        event_date = None
        for selector in date_selectors:
            date_text = response.css(f"{selector}::text").get()
            if not date_text:
                date_text = response.css(f"{selector}::attr(datetime)").get()
            if date_text:
                event_date = date_text.strip()
                break
                
        # Extract location
        location = None
        for selector in location_selectors:
            loc_text = response.css(f"{selector}::text").get()
            if loc_text:
                location = loc_text.strip()
                break
                
        # If we have enough data and it's relevant, create item
        if title and description and self._content_is_relevant(f"{title} {description}"):
            item = {
                'title': title,
                'url': response.url,
                'description': description,
                'source': urlparse(response.url).netloc,
                'type': 'event',
                'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'extraction_method': 'dynamic_selectors'
            }
            
            if event_date:
                item['date'] = event_date
                
            if location:
                item['location'] = location
                
            return item
            
        # If dynamic extraction failed, fallback to traditional methods
        return self._parse_event_details(response)
            
    def _extract_article_from_response(self, response):
        """Extract article content directly from response"""
        # Try with newspaper3k
        try:
            article = Article('')  # Empty URL
            article.set_html(response.text)
            article.parse()
            
            # Check relevance
            if not self._content_is_relevant(article.text):
                return
                
            # Create item
            item = {
                'title': article.title,
                'url': response.url,
                'text': article.text,
                'summary': article.summary,
                'source': urlparse(response.url).netloc,
                'type': 'news',
                'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'extraction_method': 'newspaper3k'
            }
            
            # Handle date
            if isinstance(article.publish_date, datetime):
                item['publish_date'] = article.publish_date.strftime("%Y-%m-%d")
            else:
                item['publish_date'] = article.publish_date
                
            # Add authors if available
            if article.authors:
                item['authors'] = article.authors
                
            # Add image if available
            if article.top_image:
                item['image_url'] = article.top_image
                
            return item
                
        except Exception as e:
            logging.error(f"Error extracting article from {response.url}: {str(e)}")
            return None

    def _parse_article_content(self, response):
        """Extract article content using newspaper3k as a fallback method"""
        try:
            article = Article(response.url)
            article.download()
            article.parse()
            
            # Extract text and check if it's relevant to our topics
            if not self._content_is_relevant(article.text):
                return
            
            # Extract publication date
            publish_date = article.publish_date
            if isinstance(publish_date, datetime):
                publish_date = publish_date.strftime("%Y-%m-%d")
            else:
                publish_date = article.publish_date  # It's already a string
            
            # Create the article item
            item = {
                'title': article.title,
                'url': response.url,
                'text': article.text,
                'summary': article.summary,
                'publish_date': publish_date,
                'source': urlparse(response.url).netloc,
                'type': response.meta.get('type', 'unknown'),
                'keywords': article.keywords,
                'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'extraction_method': 'newspaper3k_fallback'
            }
            
            # Try to get author
            if article.authors:
                item['authors'] = article.authors
            
            # Try to get image
            if article.top_image:
                item['image_url'] = article.top_image
            
            return item
            
        except Exception as e:
            logging.error(f"Error parsing article {response.url}: {str(e)}")
            return None
    
    def _parse_startup_profile(self, response):
        """Extract startup information as a fallback method"""
        # Extract using common structure patterns
        name_selectors = ["h1.name", ".company-name", ".startup-title", "h1.title"]
        name = self._get_first_match(response, name_selectors)
        
        desc_selectors = [".description", ".about", ".company-description", "meta[name=description]::attr(content)"]
        description = self._get_first_match(response, desc_selectors)
        
        # Check if the startup is relevant to our topics
        if not self._content_is_relevant(f"{name} {description}"):
            return
        
        # Process with Selenium if JavaScript rendering is needed
        if not name or not description:
            return response.follow(
                response.url,
                callback=self._parse_with_selenium,
                meta={'type': 'startup'}
            )
        
        # Create startup item
        item = {
            'name': name,
            'url': response.url,
            'description': description,
            'source': urlparse(response.url).netloc,
            'type': 'startup',
            'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extraction_method': 'traditional_fallback'
        }
        
        # Try to extract additional information
        item.update(self._extract_startup_details(response))
        
        return item
    
    def _extract_startup_details(self, response):
        """Extract additional startup details as a fallback method"""
        details = {}
        
        # Location
        location_selectors = [".location", ".address", ".country", "span.location"]
        location = self._get_first_match(response, location_selectors)
        if location:
            details['location'] = location
        
        # Founding year
        year_selectors = [".founded", ".year", ".founded-year"]
        founding_year = self._get_first_match(response, year_selectors)
        if founding_year:
            details['founding_year'] = founding_year
        
        # Funding information
        funding_selectors = [".funding", ".investment", ".raised"]
        funding = self._get_first_match(response, funding_selectors)
        if funding:
            details['funding'] = funding
        
        # Team size
        team_selectors = [".team-size", ".employees", ".team"]
        team_size = self._get_first_match(response, team_selectors)
        if team_size:
            details['team_size'] = team_size
        
        # Website
        website_selectors = ["a.website::attr(href)", ".website a::attr(href)"]
        website = self._get_first_match(response, website_selectors)
        if website:
            details['website'] = website
            
        return details
    
    def _parse_event_details(self, response):
        """Extract event information as a fallback method"""
        # Extract using common structure patterns
        title_selectors = ["h1.title", ".event-title", "h1.event-name"]
        title = self._get_first_match(response, title_selectors)
        
        desc_selectors = [".description", ".event-description", ".about-event"]
        description = self._get_first_match(response, desc_selectors)
        
        # Check if the event is relevant to our topics
        if not self._content_is_relevant(f"{title} {description}"):
            return
        
        # Process with Selenium if JavaScript rendering is needed
        if not title or not description:
            return response.follow(
                response.url,
                callback=self._parse_with_selenium,
                meta={'type': 'event'}
            )
        
        # Create event item
        item = {
            'title': title,
            'url': response.url,
            'description': description,
            'source': urlparse(response.url).netloc,
            'type': 'event',
            'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extraction_method': 'traditional_fallback'
        }
        
        # Try to extract additional information
        item.update(self._extract_event_details(response))
        
        return item
    
    def _extract_event_details(self, response):
        """Extract additional event details"""
        details = {}
        
        # Date and time
        date_selectors = [".date", ".event-date", ".datetime", "time::attr(datetime)"]
        event_date = self._get_first_match(response, date_selectors)
        if event_date:
            details['date'] = event_date
        
        # Location
        location_selectors = [".location", ".venue", ".event-location"]
        location = self._get_first_match(response, location_selectors)
        if location:
            details['location'] = location
        
        # Organizer
        organizer_selectors = [".organizer", ".host", ".event-host"]
        organizer = self._get_first_match(response, organizer_selectors)
        if organizer:
            details['organizer'] = organizer
            
        return details
    
    def _parse_generic_page(self, response):
        """Generic parsing method for websites that don't fit standard patterns"""
        # Look for article-like content
        main_content_selectors = [
            "main", "#content", ".content", "article", 
            ".main-content", "#main"
        ]
        
        main_content = None
        for selector in main_content_selectors:
            main_content = response.css(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = response.css("body")
        
        # Extract text from main content
        text = ' '.join(main_content.css("p::text, h1::text, h2::text, h3::text, h4::text").getall())
        
        # Check if the content is relevant
        if not self._content_is_relevant(text):
            # Look for links to potentially relevant content
            links = response.css("a[href*=ai], a[href*=intelligence], a[href*=startup], a[href*=africa]")
            for link in links:
                href = link.css("::attr(href)").get()
                if href and self._url_seems_relevant(href):
                    yield response.follow(
                        href,
                        callback=self.parse
                    )
            return
        
        # Create a generic content item
        title_selectors = ["h1", "title", ".headline", ".page-title"]
        title = self._get_first_match(response, title_selectors) or "Unknown Title"
        
        item = {
            'title': title,
            'url': response.url,
            'text': text,
            'source': urlparse(response.url).netloc,
            'type': 'generic',
            'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'extraction_method': 'generic_parser'
        }
        
        return item
    
    def _parse_with_selenium(self, response):
        """Use Selenium for JavaScript-rendered pages"""
        try:
            if not self.driver:
                self.driver = webdriver.Chrome(service=self.service, options=self.options)
            
            self.driver.get(response.url)
            time.sleep(5)  # Allow time for JavaScript to render
            
            page_source = self.driver.page_source
            sel_response = scrapy.Selector(text=page_source)
            
            # Feed the rendered page to our selector learner
            content_type = response.meta.get('type', 'generic')
            self.selector_learner.analyze_page(page_source, content_type)
            
            # Determine content type from meta
            if content_type == 'news':
                # First try with dynamic selectors
                title_selectors = self.selector_learner.get_selectors('title', 'news')
                content_selectors = self.selector_learner.get_selectors('content', 'news')
                
                title = None
                for selector in title_selectors:
                    title = sel_response.css(f"{selector}::text").get()
                    if title:
                        title = title.strip()
                        break
                        
                content = None
                for selector in content_selectors:
                    paragraphs = sel_response.css(f"{selector} p::text").getall()
                    if paragraphs:
                        content = ' '.join(paragraphs).strip()
                        break
                
                # If dynamic extraction worked and content is relevant
                if title and content and self._content_is_relevant(f"{title} {content}"):
                    item = {
                        'title': title,
                        'url': response.url,
                        'text': content,
                        'source': urlparse(response.url).netloc,
                        'type': 'news',
                        'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'extraction_method': 'dynamic_selectors_selenium'
                    }
                    return item
                
                # Fallback to newspaper3k
                article = Article(response.url)
                article.set_html(page_source)
                article.parse()
                
                if not self._content_is_relevant(article.text):
                    return
                
                item = {
                    'title': article.title,
                    'url': response.url,
                    'text': article.text,
                    'summary': article.summary,
                    'source': urlparse(response.url).netloc,
                    'type': 'news',
                    'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'extraction_method': 'newspaper3k_selenium'
                }
                
                if isinstance(article.publish_date, datetime):
                    item['publish_date'] = article.publish_date.strftime("%Y-%m-%d")
                else:
                    item['publish_date'] = article.publish_date
                if article.authors:
                    item['authors'] = article.authors
                
                return item
                
            elif content_type == 'startup':
                # Try with dynamic selectors first
                name_selectors = self.selector_learner.get_selectors('name', 'startup')
                desc_selectors = self.selector_learner.get_selectors('description', 'startup')
                
                name = None
                for selector in name_selectors:
                    name = sel_response.css(f"{selector}::text").get()
                    if name:
                        name = name.strip()
                        break
                        
                description = None
                for selector in desc_selectors:
                    desc_text = sel_response.css(f"{selector}::text").get()
                    if not desc_text:
                        desc_paragraphs = sel_response.css(f"{selector} p::text").getall()
                        if desc_paragraphs:
                            desc_text = ' '.join(desc_paragraphs)
                    if desc_text:
                        description = desc_text.strip()
                        break
                
                # If we got good data with selectors, use it
                if name and description and self._content_is_relevant(f"{name} {description}"):
                    item = {
                        'name': name,
                        'url': response.url,
                        'description': description,
                        'source': urlparse(response.url).netloc,
                        'type': 'startup',
                        'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'extraction_method': 'dynamic_selectors_selenium'
                    }
                    return item
                
                # Fallback to traditional extraction
                name_selectors = ["h1.name", ".company-name", ".startup-title", "h1"]
                name = self._get_first_match(sel_response, name_selectors)
                
                desc_selectors = [".description", ".about", "p", ".company-description"]
                description = self._get_first_match(sel_response, desc_selectors)
                
                if not self._content_is_relevant(f"{name} {description}"):
                    return
                
                item = {
                    'name': name,
                    'url': response.url,
                    'description': description,
                    'source': urlparse(response.url).netloc,
                    'type': 'startup',
                    'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'extraction_method': 'traditional_selenium'
                }
                
                # Try to extract additional details
                location_selectors = [".location", ".address", ".country"]
                location = self._get_first_match(sel_response, location_selectors)
                if location:
                    item['location'] = location
                
                return item
                
            elif content_type == 'event':
                # Try with dynamic selectors first
                title_selectors = self.selector_learner.get_selectors('title', 'event')
                desc_selectors = ['.description', '.event-description', '.about']
                
                title = None
                for selector in title_selectors:
                    title = sel_response.css(f"{selector}::text").get()
                    if title:
                        title = title.strip()
                        break
                        
                description = None
                for selector in desc_selectors:
                    desc_text = sel_response.css(f"{selector}::text").get()
                    if not desc_text:
                        desc_paragraphs = sel_response.css(f"{selector} p::text").getall()
                        if desc_paragraphs:
                            desc_text = ' '.join(desc_paragraphs)
                    if desc_text:
                        description = desc_text.strip()
                        break
                
                # If we got good data with selectors, use it
                if title and description and self._content_is_relevant(f"{title} {description}"):
                    item = {
                        'title': title,
                        'url': response.url,
                        'description': description,
                        'source': urlparse(response.url).netloc,
                        'type': 'event',
                        'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'extraction_method': 'dynamic_selectors_selenium'
                    }
                    return item
                
                # Fallback to traditional methods
                title_selectors = ["h1.title", ".event-title", "h1"]
                title = self._get_first_match(sel_response, title_selectors)
                
                desc_selectors = [".description", ".event-description", "p"]
                description = self._get_first_match(sel_response, desc_selectors)
                
                if not self._content_is_relevant(f"{title} {description}"):
                    return
                
                item = {
                    'title': title,
                    'url': response.url,
                    'description': description,
                    'source': urlparse(response.url).netloc,
                    'type': 'event',
                    'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'extraction_method': 'traditional_selenium'
                }
                
                # Try to extract additional details
                date_selectors = [".date", ".event-date", "time"]
                event_date = self._get_first_match(sel_response, date_selectors)
                if event_date:
                    item['date'] = event_date
                
                location_selectors = [".location", ".venue", ".address"]
                location = self._get_first_match(sel_response, location_selectors)
                if location:
                    item['location'] = location
                
                return item
            
        except Exception as e:
            logging.error(f"Selenium error processing {response.url}: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _extract_pagination(self, response):
        """Extract next page URL for pagination"""
        # Common pagination selectors
        next_page_selectors = [
            "a.next::attr(href)", 
            ".pagination a.next::attr(href)",
            "a:contains('Next')::attr(href)",
            "a[rel=next]::attr(href)",
            ".pagination a[aria-label=Next]::attr(href)"
        ]
        
        for selector in next_page_selectors:
            try:
                next_page = response.css(selector).get()
                if next_page:
                    return response.urljoin(next_page)
            except:
                continue
        
        return None
    
    def _get_first_match(self, response, selectors):
        """Try multiple selectors and return the first match"""
        for selector in selectors:
            try:
                if "::attr" in selector:
                    result = response.css(selector).get()
                else:
                    result = response.css(f"{selector}::text").get()
                    if not result:
                        result = response.css(selector).get()
                
                if result:
                    return result.strip()
            except:
                continue
        
        return None
        
    def _content_is_relevant(self, text):
        """Check if content contains AI keywords and African references"""
        if not text:
            return False
            
        text = text.lower()
        
        # Check for AI relevance
        has_ai_keywords = any(keyword.lower() in text for keyword in self.ai_keywords)
        
        # Check for African relevance
        has_african_reference = any(country.lower() in text for country in self.african_countries)
        
        return has_ai_keywords and has_african_reference
    
    def _url_seems_relevant(self, url):
        """Quick check if URL seems relevant to our topics"""
        url_lower = url.lower()
        
        # Check for AI relevance in URL
        has_ai_keywords = any(keyword.lower().replace(" ", "-") in url_lower or 
                              keyword.lower().replace(" ", "") in url_lower 
                              for keyword in self.ai_keywords)
        
        # Check for African relevance in URL
        has_african_reference = any(country.lower().replace(" ", "-") in url_lower or
                                   country.lower().replace(" ", "") in url_lower 
                                   for country in self.african_countries)
        
        # Ignore mailto links and other non-http schemes
        if url_lower.startswith('mailto:') or not (url_lower.startswith('http://') or url_lower.startswith('https://')):
            return False
        
        # More lenient check for URL relevance
        return has_ai_keywords or has_african_reference

class JsonExportPipeline:
    """Pipeline to export items to a JSON file"""
    
    def __init__(self):
        self.file = open('africa_ai_data.json', 'w', encoding='utf-8')
        self.file.write('[')
        self.first_item = True
        self.items_count = 0
        self.start_time = datetime.now()
    
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False)
        if self.first_item:
            self.first_item = False
        else:
            line = ',\n' + line
        self.file.write(line)
        
        # Log progress
        self.items_count += 1
        if self.items_count % 10 == 0:
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            logging.info(f"Processed {self.items_count} items in {elapsed:.2f} minutes")
        
        return item
    
    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()
        
        # Log final stats
        elapsed = (datetime.now() - self.start_time).total_seconds() / 60
        logging.info(f"Scraper finished. Processed {self.items_count} items in {elapsed:.2f} minutes")
        logging.info(f"Domains processed: {len(spider.processed_domains)}")
        logging.info(f"Learned selectors for page types: {', '.join(spider.selector_learner.learned_selectors.keys())}")

def clean_text(text):
    """Clean and normalize extracted text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    return text

# Run the spider
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("scraper.log"),
            logging.StreamHandler()
        ]
    )
    
    try:
        # Create and run the crawler process
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        })
        process.crawl(AfricaAISpider)
        process.start()
        
        logging.info("Scraper completed successfully")
        
    except Exception as e:
        logging.error(f"Error running scraper: {str(e)}")