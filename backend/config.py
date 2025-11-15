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

# Model Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# Gemini model options: "gemini-1.5-flash" (faster), "gemini-1.5-pro" (more capable)
GEMINI_MODEL = "gemini-1.5-flash"

# RAG Configuration
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 3
SIMILARITY_THRESHOLD = 0.7

# LLM Configuration
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Vector Store Configuration
VECTOR_STORE_INDEX_FILE = VECTOR_STORE_DIR / "faiss_index.index"
VECTOR_STORE_METADATA_FILE = VECTOR_STORE_DIR / "metadata.json"

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

