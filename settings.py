from datetime import date

DEBUG_MODE = False


# Rate limiting settings
MIN_DELAY_S: float = 1
MAX_DELAY_S: float = 3
MAX_WORKERS = 5  # For thread pool

# Llm settings
GEMINI_MODEL = "gemini-2.0-flash"
MAX_OUTPUT_TOKENS = 8192


WORKERS_COUNT = 6

PORT = "3015"

LAST_FETCH_DATE = date(
    year=2020,
    month=1,
    day=1,
)
