# Gemini API Only Configuration

The system has been configured to use **Gemini API exclusively** for all LLM operations.

## Changes Made

### 1. Backend Updates

- **`backend/llm.py`**: 
  - Removed support for OpenAI and HuggingFace
  - Only accepts "gemini" as provider
  - Simplified initialization to only require Gemini API key

- **`backend/rag_pipeline.py`**: 
  - Default provider changed from "openai" to "gemini"

- **`backend/api.py`**: 
  - Removed fallback logic to other providers
  - Always uses Gemini

- **`backend/config.py`**: 
  - Removed OpenAI and HuggingFace API key configurations
  - Removed OpenAI and HuggingFace model configurations
  - Only keeps Gemini configuration

### 2. Frontend Updates

- **`frontend/app.py` (Streamlit)**: 
  - Removed provider selection dropdown
  - Shows info message that Gemini is configured via GEMINI_API_KEY
  - Removed fallback logic to other providers

## Configuration

### Required: `.env` File

Create a `.env` file in `Capstone_project/` with:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## Usage

The system will now:
- ✅ Always use Gemini for question answering
- ✅ Always use Gemini for document summarization
- ✅ Require GEMINI_API_KEY to be set
- ❌ No longer support OpenAI or HuggingFace

## Error Messages

If Gemini API key is not found, you'll see:
```
ValueError: Gemini API key not found. Set GEMINI_API_KEY in environment or .env file.
```

## Benefits

- Simpler configuration (only one API key needed)
- Consistent behavior across all operations
- Reduced dependencies
- Clearer error messages

---

**Note**: The OpenAI and HuggingFace code has been removed from the LLM wrapper, but the libraries remain in requirements.txt for potential future use. You can remove them if desired.

