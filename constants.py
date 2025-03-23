# Constants and configuration
from dtypes.source import Source

NEWS_PROMPTS_MD_PATH = "./prompts/news_prompt.md"
AI_TRIGGER_WORDS_PATH = "./data/ai/trigger_words.txt"
AI_TRIGGER_PHRASES_PATH = "./data/ai/trigger_phrases.txt"
AFRICA_TRIGGER_WORDS_PATH = "./data/africa/trigger_words.txt"
AFRICA_TRIGGER_PHRASES_PATH = "./data/africa/trigger_phrases.txt"
SOURCES: list[Source] = [
    # {
    #     "selectors": {
    #         "next_button": None,
    #         "title": "header > h3 > a",
    #         "link": "header > h3 > a",
    #         "load_more_button": "a[data-g1-next-page-url]",
    #         "author": {
    #             "link": ".entry-author > a",
    #             "name": "strong[itemprop='name']",
    #         },
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
    # {
    #     "url": "https://um6p.ma/actualites",
    #     "selectors": {
    #         "next_button": ".pager__item--next > a",
    #         "title": ".post-title > a",
    #         "link": ".post-title > a",
    #         "author": None,
    #         "load_more_button": None,
    #     },
    #     "trigger_africa": False,
    #     "trigger_ai": True,
    # },
    {
        "url": "https://www.up.ac.za/news",
        "selectors": {
            # "title": ".news-list-item h3 a",
            # "link": ".news-list-item h3 a::attr(href)",
            # "load_more_button": None,  # No load more button in the provided HTML
            # "next_button": ".pagination .next a::attr(href)", # Assuming there's a pagination with a 'next' button
            "title": "ul.row.news-list > li > a > h4",
            "link": "ul.row.news-list > li > a",
            "load_more_button": None,
            "next_button": "div.zp_pager_links > ul > li.next > a",
            # "author": None,
        },
        "trigger_africa": False,
        "trigger_ai": True,
    },
]
