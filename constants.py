NEWS_PROMPTS_PATH = "./prompts/news_prompt.md"
NEWS_DETAIL_PROMPTS_PATH = "./prompts/news_detail_prompt.md"
SUMMARY_PROMPT_PATH = "./prompts/summary_prompt.md"


AI_TRIGGER_WORDS_PATH = "./data/ai/trigger_words.txt"
AI_TRIGGER_PHRASES_PATH = "./data/ai/trigger_phrases.txt"
AFRICA_TRIGGER_WORDS_PATH = "./data/africa/trigger_words.txt"
AFRICA_TRIGGER_PHRASES_PATH = "./data/africa/trigger_phrases.txt"

CATEGORY_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT NULL
);
"""

STATISTICS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS statistics (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT UNIQUE NOT NULL,
    stats JSONB,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT NULL
);
"""

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
    sourceId BIGINT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    categoryId BIGINT DEFAULT NULL REFERENCES categories(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    authorId BIGINT REFERENCES authors(id) ON DELETE SET NULL,
    body TEXT NOT NULL,
    postDate TIMESTAMP WITH TIME ZONE,
    imageUrl TEXT,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

TRIGGER_WORDS_CATEGORIES: dict[str, list[str]] = {
        "Research": [
            "study",
            "research",
            "paper",
            "publication",
            "findings",
            "experiment",
            "scientific",
            "peer-reviewed",
            "hypothesis",
            "methodology",
            "data analysis",
            "academic",
            "scholarly",
        ],
        "AI Tools": [
            "tool",
            "software",
            "platform",
            "application",
            "framework",
            "library",
            "API",
            "SDK",
            "plugin",
            "extension",
            "utility",
            "package",
            "module",
            "interface",
        ],
        "Industry": [
            "enterprise",
            "business",
            "corporation",
            "industry",
            "market",
            "sector",
            "commercial",
            "manufacturing",
            "supply chain",
            "logistics",
            "retail",
            "finance",
            "automotive",
        ],
        "Startups": [
            "startup",
            "venture",
            "funding",
            "seed round",
            "accelerator",
            "incubator",
            "founder",
            "pitch",
            "angel investor",
            "VC",
            "bootstrapped",
            "unicorn",
            "scaleup",
            "disrupt",
        ],
        "Regulation": [
            "law",
            "regulation",
            "policy",
            "legislation",
            "compliance",
            "governance",
            "oversight",
            "standard",
            "guideline",
            "framework",
            "enforcement",
            "audit",
            "certification",
        ],
        "Ethics": [
            "ethical",
            "bias",
            "fairness",
            "privacy",
            "transparency",
            "accountability",
            "responsibility",
            "trustworthy",
            "equity",
            "inclusion",
            "diversity",
            "sustainability",
            "human rights",
        ],
        "Health": [
            "medical",
            "healthcare",
            "diagnosis",
            "treatment",
            "patient",
            "hospital",
            "biomedical",
            "clinical",
            "pharmaceutical",
            "telemedicine",
            "wearable",
            "genomics",
            "prognosis",
        ],
        "Robotics": [
            "robot",
            "drone",
            "automation",
            "mechanical",
            "actuator",
            "sensor",
            "manipulator",
            "autonomous",
            "cobot",
            "exoskeleton",
            "swarm",
            "kinematics",
            "end effector",
        ],
        "AGI": [
            "artificial general intelligence",
            "AGI",
            "superintelligence",
            "consciousness",
            "human-level AI",
            "cognitive architecture",
            "theory of mind",
            "self-awareness",
            "reasoning",
            "learning",
            "adaptation",
        ],
        "NLP": [
            "natural language processing",
            "NLP",
            "language model",
            "translation",
            "sentiment analysis",
            "text generation",
            "speech recognition",
            "chatbot",
            "transformer",
            "tokenization",
            "parsing",
            "semantics",
        ],
        "Computer Vision": [
            "computer vision",
            "image recognition",
            "object detection",
            "facial recognition",
            "visual perception",
            "segmentation",
            "classification",
            "feature extraction",
            "optical flow",
            "depth estimation",
            "pose estimation",
        ],
        "AI Art": [
            "AI art",
            "generative art",
            "creative AI",
            "digital art",
            "neural style transfer",
            "DALL-E",
            "Stable Diffusion",
            "Midjourney",
            "GAN",
            "procedural generation",
            "algorithmic art",
            "computational creativity",
        ],
        "Opinion": [
            "opinion",
            "perspective",
            "viewpoint",
            "analysis",
            "commentary",
            "editorial",
            "thoughts",
            "reflection",
            "critique",
            "review",
            "take",
            "position",
            "argument",
        ],
    }
