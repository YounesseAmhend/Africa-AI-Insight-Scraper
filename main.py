from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

from dtypes.source import Source
from utils.trigger_file import TriggerFile


app = FastAPI()

ai_trigger_words_path = "data/ai/trigger_words.txt"
ai_trigger_phrases_path = "data/ai/trigger_phrases.txt"
africa_trigger_words_path = "data/africa/trigger_words.txt"
africa_trigger_phrases_path = "data/africa/trigger_phrases.txt"

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
        "selector": "header > h3 > a",
        "trigger_phrases": trigger_phrases_africa,
        "trigger_words": trigger_words_africa,
        "url": "https://aipressroom.com/events/",
    },
]


@app.get("/")
def root():
    for source in sources:
        url = source["url"]
        trigger_phrases = source["trigger_phrases"]
        trigger_words = source["trigger_words"]
        selector = source["selector"]
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.select(selector)

        result: list[dict[str, str]] = []
        for i, element in enumerate(elements):
            text = element.get_text()
            words = text.split()
            for trigger_word in trigger_words:
                if trigger_word in words:
                    result.append({f"{i}": text})

            for trigger_phrase in trigger_phrases:
                if trigger_phrase in text:
                    result.append({f"{i}": text})

    print(result)
    return result


@app.post("/")
def he():
    return {"Some data": "dataefddd"}
