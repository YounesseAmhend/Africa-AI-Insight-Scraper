from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

from source import Source


app = FastAPI()
trigger_words_ai = [
    "AI",
    "LLM",
]

trigger_phrases_ai = [
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Neural Network",
    "Natural Language Processing",
    "Computer Vision",
    "Generative AI",
    "Large Language Model",
]

trigger_words_africa = [
    "Africa",
    "African",
    "Afrika",
    "Afrikan",
    "Afro",
    "Sub-Saharan",
    "Maghreb",
    "Sahel",
    "Horn of Africa",
    "Algeria",
    "Angola",
    "Benin",
    "Botswana",
    "Burkina Faso",
    "Burundi",
    "Cameroon",
    "Cape Verde",
    "Central African Republic",
    "Chad",
    "Comoros",
    "Congo",
    "Côte d'Ivoire",
    "Djibouti",
    "Egypt",
    "Equatorial Guinea",
    "Eritrea",
    "Eswatini",
    "Ethiopia",
    "Gabon",
    "Gambia",
    "Ghana",
    "Guinea",
    "Guinea-Bissau",
    "Kenya",
    "Lesotho",
    "Liberia",
    "Libya",
    "Madagascar",
    "Malawi",
    "Mali",
    "Mauritania",
    "Mauritius",
    "Morocco",
    "Mozambique",
    "Namibia",
    "Niger",
    "Nigeria",
    "Rwanda",
    "Sao Tome and Principe",
    "Senegal",
    "Seychelles",
    "Sierra Leone",
    "Somalia",
    "South Africa",
    "South Sudan",
    "Sudan",
    "Tanzania",
    "Togo",
    "Tunisia",
    "Uganda",
    "Zambia",
    "Zimbabwe",
]

trigger_phrases_africa = [
    "West Africa",
    "East Africa",
    "North Africa",
    "Southern Africa",
    "Central Africa",
    "African Union",
    "African Development",
    "African Culture",
    "African History",
    "African Economy",
    "African Politics",
    "African Wildlife",
    "African Diaspora",
    "Pan-African",
    "African Renaissance",
]

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
