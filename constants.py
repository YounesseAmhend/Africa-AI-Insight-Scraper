# Constants and configuration
from dtypes.source_dict import SourceDict

NEWS_PROMPTS_PATH = "./prompts/news_prompt.md"
NEWS_DETAIL_PROMPTS_PATH = "./prompts/news_detail_prompt.md"


AI_TRIGGER_WORDS_PATH = "./data/ai/trigger_words.txt"
AI_TRIGGER_PHRASES_PATH = "./data/ai/trigger_phrases.txt"
AFRICA_TRIGGER_WORDS_PATH = "./data/africa/trigger_words.txt"
AFRICA_TRIGGER_PHRASES_PATH = "./data/africa/trigger_phrases.txt"


SOURCE_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    selector JSONB,
    triggerAfrica BOOLEAN NOT NULL,
    triggerAi BOOLEAN NOT NULL,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT NULL
);
"""

AUTHORS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT UNIQUE,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

NEWS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    sourceId INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    authorId INTEGER REFERENCES authors(id) ON DELETE SET NULL,
    body TEXT NOT NULL,
    postDate TIMESTAMP WITH TIME ZONE,
    imageUrl TEXT,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""