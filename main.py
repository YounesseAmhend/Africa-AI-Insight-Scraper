from time import sleep

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from selenium.webdriver.support import expected_conditions as EC

from dtypes.author import Author
from dtypes.source import Source
from utils.my_driver import MyDriver
from urllib.parse import urlparse

from utils.trigger_file import TriggerFile

app = FastAPI()


AI_TRIGGER_WORDS_PATH = "./data/ai/trigger_words.txt"
AI_TRIGGER_PHRASES_PATH = "./data/ai/trigger_phrases.txt"
AFRICA_TRIGGER_WORDS_PATH = "./data/africa/trigger_words.txt"
AFRICA_TRIGGER_PHRASES_PATH = "./data/africa/trigger_phrases.txt"

ai_trigger_words = TriggerFile(AI_TRIGGER_WORDS_PATH)
ai_trigger_phrases = TriggerFile(AI_TRIGGER_PHRASES_PATH)
africa_trigger_words = TriggerFile(AFRICA_TRIGGER_WORDS_PATH)
africa_trigger_phrases = TriggerFile(AFRICA_TRIGGER_PHRASES_PATH)

trigger_words_ai = ai_trigger_words.get()
trigger_phrases_ai = ai_trigger_phrases.get()
trigger_words_africa = africa_trigger_words.get()
trigger_phrases_africa = africa_trigger_phrases.get()

HEADERS = {"User-Agent": "Mozilla/5.0"}

sources: list[Source] = [
    # {
    #     "selectors": {
    #         "next_button": None,
    #         "title": "header > h3 > a",
    #         "link": "header > h3 > a",
    #         "author": {
    #             "link": ".entry-author > a",
    #             "name": "strong[itemprop='name']",
    #         },
    #         "load_more_button": "a[data-g1-next-page-url]",
    #     },
    #     "url": "https://aipressroom.com/events/",
    #     "trigger_africa": True,
    #     "trigger_ai": False,
    # },
    # {
    #     "selectors": {
    #         "next_button": None,
    #         "title": "#event-card-in-search-results > h2",
    #         "link": "#event-card-in-search-results",
    #         "author": {
    #             "link": None,
    #             "name": '[data-event-label="hosted-by"] div:nth-of-type(2) > div:last-child',
    #         },
    #         "load_more_button": None,
    #     },
    #     "url": "https://www.meetup.com/find/",
    #     "trigger_africa": True,
    #     "trigger_ai": True,
    # },
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
]


@app.get("/")
def root():
    all_results: list[dict] = []
    for source in sources:
        print(f"Processing source: {source['url']}")
        
        url = source["url"]
        trigger_ai = source["trigger_ai"]
        trigger_africa = source["trigger_africa"]
        selector = source["selectors"]
        
        author_selector = selector["author"]
        next_button_selector = selector['next_button']
        load_more_selector = selector["load_more_button"]
        
        print(f"Navigating to URL: {url}")
        html: str = ""
        MyDriver.get(url)
        
        if next_button_selector is None:
            print(f"No pagination found. Using scroll to end with load_more_selector: {load_more_selector}")
            MyDriver.scroll_to_end(load_more_selector, timeout_s=10)
            html = MyDriver.get_html()
        else:
            print(f"Pagination found. Using next button selector: {next_button_selector}")
            html = MyDriver.handle_pagination(next_button_selector, timeout_s=10)
        
        print("Parsing HTML with BeautifulSoup")
        soup = BeautifulSoup(html, "html.parser")

        print(f"Selecting elements with selector: {selector['title']}")
        elements = soup.select(selector["title"])
        print(f"Found {len(elements)} title elements")
        
        print(f"Selecting links with selector: {selector['link']}")
        links = soup.select(selector["link"])
        print(f"Found {len(links)} link elements")

        # assert(len(links) == len(elements))

        source_results = []  # Create a list for results from this source
        print(f"Processing {len(elements)} elements")

        for i, element in enumerate(elements):
            print(f"Processing element {i+1}/{len(elements)}")
            title = element.get_text()
            link = links[i].get("href")
            link = str(link)
            # Check if link is relative (starts with /) and make it absolute
            if link and link.startswith('/'):
                # Extract domain from the source URL
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = f"{base_url}{link}"
                
            print(f"Title: {title}")
            print(f"Link: {link}")

            # Check for trigger words or phrases
            should_add_africa = False

            # Function to check if text contains any trigger words or phrases
            def contains_triggers(text: str, trigger_words: list[str], trigger_phrases: list[str],) -> bool:
                words = text.split()
                for word in trigger_words:
                    if word.lower() in [w.lower() for w in words]:
                        return True
                # Check for trigger phrases
                for phrase in trigger_phrases:
                    if phrase.lower() in text.lower():
                        return True
                return False

            # Check for Africa triggers if needed
            should_add_africa = False
            if trigger_africa:
                print(f"Checking for Africa triggers in: {title}")
                
                should_add_africa = contains_triggers(
                    title, 
                    trigger_words_africa, 
                    trigger_phrases_africa,
                )
                if "africa" in title.lower():
                    print(f"Found Africa keyword in: {title}")
            
            # Check for AI triggers if needed
            should_add_ai = False
            if trigger_ai:
                print(f"Checking for AI triggers in: {title}")
                should_add_ai = contains_triggers(
                    title, 
                    trigger_words_ai, 
                    trigger_phrases_ai,
                )
                if should_add_ai:
                    print(f"Found AI trigger in: {title}")
            
            # Determine if we should add this result based on trigger requirements
            should_add = (
                should_add_ai == trigger_ai and should_add_africa == trigger_africa
            )
            print(f"Should add this result: {should_add}")
            
            # Add the result if it matches any trigger
            if should_add:
                if link is None:
                    print("Skipping - link is None")
                    continue
                    
                print(f"Fetching author information from: {link}")
                author_response = requests.get(url=link, headers=HEADERS)
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                author: Author | None = None
                
                if author_selector is not None:
                    print(f"Looking for author with selector: {author_selector}")
                    author_name_element = author_soup.select_one(
                        str(author_selector["name"])
                    )
                    author_link_element = author_soup.select_one(
                        str(author_selector["link"])
                    )

                    author = {
                        "name": (
                            author_name_element.get_text()
                            if author_name_element
                            else "Unknown"
                        ),
                        "link": (
                            str(author_link_element.get("href"))
                            if author_link_element
                            else None
                        ),
                    }
                    print(f"Found author: {author['name']}")

                print(f"Adding result: {title}")
                source_results.append(
                    {
                        "title": title,
                        "link": link,
                        "author": author,
                    }
                )

        # Add results from this source to the overall results
        print(f"Adding {len(source_results)} results from {url} to all_results")
        all_results.extend(source_results)

    print(f"Total results found: {len(all_results)}")
    print(all_results)
    return all_results
