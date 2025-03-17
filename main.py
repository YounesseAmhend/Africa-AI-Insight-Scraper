import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

from dtypes.source import Source
from utils.trigger_file import TriggerFile

app = FastAPI()

ai_trigger_words_path = "./data/ai/trigger_words.txt"
ai_trigger_phrases_path = "./data/ai/trigger_phrases.txt"
africa_trigger_words_path = "./data/africa/trigger_words.txt"
africa_trigger_phrases_path = "./data/africa/trigger_phrases.txt"

ai_trigger_words = TriggerFile(ai_trigger_words_path)
ai_trigger_phrases = TriggerFile(ai_trigger_phrases_path)
africa_trigger_words = TriggerFile(africa_trigger_words_path)
africa_trigger_phrases = TriggerFile(africa_trigger_phrases_path)

trigger_words_ai = ai_trigger_words.get()
trigger_phrases_ai = ai_trigger_phrases.get()
trigger_words_africa = africa_trigger_words.get()
trigger_phrases_africa = africa_trigger_phrases.get()

headers = {"User-Agent": "Mozilla/5.0"}

sources: list[Source] = [
    {
        "selector": {
            "title":"header > h3 > a",
            "link": "header > h3 > a",
            "author":{
                "link": ".entry-author > a",
                "name": "strong[itemprop='name']",
                },
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
        selector = source["selector"]
        author_selector= selector["author"]
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
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
                author_response = requests.get(url=link, headers=headers)
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
