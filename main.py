from time import sleep

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from selenium.webdriver.support import expected_conditions as EC

from dtypes.source import Source
from utils.my_driver import MyDriver
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
    {
        "selectors": {
            "title":"header > h3 > a",
            "link": "header > h3 > a",
            "author":{
                "link": ".entry-author > a",
                "name": "strong[itemprop='name']",
                },
            "load_more_button": "a[data-g1-next-page-url]",
            },
        "trigger_phrases": trigger_phrases_africa,
        "trigger_words": trigger_words_africa,
        "url": "https://aipressroom.com/events/",
    },
]


@app.get("/")
def root():
    all_results: list[dict] = [] 
    
    
    
    for source in sources:
        url = source["url"]
        trigger_phrases = source["trigger_phrases"]
        trigger_words = source["trigger_words"]
        selector = source["selectors"]
        author_selector= selector["author"]
        
        MyDriver.get(url)
        MyDriver.scroll_to_end(selector["load_more_button"], timeout_s=10)
        html = MyDriver.get_html()
        soup = BeautifulSoup(html, "html.parser")
        
        elements = soup.select(selector["title"])
        links = soup.select(selector["link"])
        
        assert(len(links) == len(elements))
        
        source_results = []  # Create a list for results from this source
        
        for i, element in enumerate(elements):
            title = element.get_text()
            words = title.split()
            link = links[i].get('href')
            
            # Check for trigger words or phrases
            should_add = False
            
            for trigger_word in trigger_words:
                if trigger_word in words:
                    should_add = True
                    break
                    
            if not should_add:  # Only check phrases if we haven't found a trigger word
                for trigger_phrase in trigger_phrases:
                    if trigger_phrase in title:
                        should_add = True
                        break
            
            # Add the result if it matches any trigger
            if should_add:
                if link is None:
                    continue
                link = str(link)
                author_response = requests.get(url=link, headers=HEADERS)
                author_soup = BeautifulSoup(author_response.text, "html.parser")
                
                author_name_element = author_soup.select_one(author_selector["name"])
                author_link_element = author_soup.select_one(author_selector["link"])
                
                if (author_link_element is None or author_name_element is None):
                    return # just for type safety
                author = {
                    "name": author_name_element.get_text(),
                    "link": author_link_element.get("href"),
                } 
                
                
                
                source_results.append({
                    "title": title,
                    "link": link,
                    "author": author,
                })
        
        # Add results from this source to the overall results
        all_results.extend(source_results)
    
    print(all_results)
    return all_results



@app.post("/")
def he():
    return {"Some data": "dataefddd"}
