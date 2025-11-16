"""
Configuration file for the RAG Document Knowledge Assistant.
Handles environment variables, API keys, and global constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# Ensure directories exist
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# Gemini model: Use "gemini-flash-latest" (stable) or "gemini-2.5-flash" (newer)
GEMINI_MODEL = "gemini-flash-latest"
# Claude model (Haiku 4.5)
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4.5")

# RAG Configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 3
SIMILARITY_THRESHOLD = 0.7

# LLM Configuration
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Default LLM provider used across the application (set to 'claude' to enable Claude Haiku 4.5)
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "claude")

# Vector Store Configuration
VECTOR_STORE_INDEX_FILE = VECTOR_STORE_DIR / "faiss_index.index"
VECTOR_STORE_METADATA_FILE = VECTOR_STORE_DIR / "metadata.json"

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

