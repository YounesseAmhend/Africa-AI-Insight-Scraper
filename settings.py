DEBUG_MODE = True


# Rate limiting settings
MIN_DELAY_S: float = 1
MAX_DELAY_S: float = 3
MAX_WORKERS = 5  # For thread pool

# Llm settings
GEMINI_MODEL = "gemini-2.0-flash"
MAX_TOKENS = 8192


GRPC_ADDRESS = 'localhost:50051'
