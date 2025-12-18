"""
Global configuration settings for Lamp of Knowledge.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Options: "openai" or "groq"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Narration Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))  # Characters per narration chunk
NARRATION_DELAY = float(os.getenv("NARRATION_DELAY", "0.5"))  # Seconds between chunks

# Path Configuration
RFID_MAPPING_FILE = BASE_DIR / "data" / "rfid_books.json"
BOOKS_DIR = BASE_DIR / "data" / "books"

# Session Configuration
SESSION_PERSISTENCE = os.getenv("SESSION_PERSISTENCE", "false").lower() == "true"
SESSION_FILE = BASE_DIR / "data" / "session.json"

# API Configuration
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # Seconds
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", "3"))
API_RETRY_DELAY = float(os.getenv("API_RETRY_DELAY", "1.0"))  # Seconds

# Question Answering Configuration
CONTEXT_CHUNKS_BEFORE = int(os.getenv("CONTEXT_CHUNKS_BEFORE", "2"))
CONTEXT_CHUNKS_AFTER = int(os.getenv("CONTEXT_CHUNKS_AFTER", "2"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "data" / "lamp_of_knowledge.log"

# Chapter Detection Configuration
MIN_FRONT_MATTER_SKIP = 0.05  # Skip at least 5% of document (typical front matter)
MAX_FRONT_MATTER_SKIP = 0.30  # Skip at most 30% of document

