# Intelligent Document Knowledge Assistant

A complete end-to-end RAG (Retrieval-Augmented Generation) system that allows users to upload documents, extract knowledge, and interact with them through an intelligent chat interface.

## 🎯 Features

- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Intelligent Text Extraction**: Automatic text extraction from various document formats
- **Vector Search**: FAISS-based semantic search for efficient retrieval
- **RAG Pipeline**: Complete retrieval-augmented generation workflow
- **Chat Interface**: Clean, modern chat UI for question-answering
- **Multi-Document Summarization**: Generate comprehensive summaries across all documents
- **Multiple LLM Support**: Gemini (default), OpenAI, and HuggingFace integration

## 🏗️ Architecture

```
Capstone_project/
├── backend/
│   ├── config.py          # Configuration and environment variables
│   ├── file_parser.py     # Document text extraction
│   ├── embeddings.py      # SentenceTransformers embeddings
│   ├── vector_store.py    # FAISS vector store management
│   ├── llm.py             # LLM API wrappers (OpenAI/HuggingFace)
│   └── rag_pipeline.py    # Complete RAG orchestration
├── frontend/
│   └── app.py             # Streamlit web application
├── data/
│   ├── documents/         # Uploaded document storage
│   └── vector_store/     # FAISS index and metadata
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 📋 Prerequisites

- Python 3.8 or higher
- Gemini API key (default, recommended) OR OpenAI API key OR HuggingFace API key

## 🚀 Setup

### 1. Clone or Download the Project

Navigate to the project directory:
```bash
cd Capstone_project
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Create a `.env` file in the `Capstone_project` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note:** The system defaults to Gemini. You can also use OpenAI or HuggingFace by adding their API keys and selecting them in the UI:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### 5. Run the Application

```bash
streamlit run frontend/app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 How to Use

### 1. Upload Documents

1. Navigate to the **"Upload Documents"** tab
2. Click "Choose files" and select PDF, DOCX, or TXT files
3. Click "Process" for each file to extract text, generate embeddings, and add to the vector store
4. Wait for the success message confirming processing

### 2. Ask Questions

1. Navigate to the **"Chat"** tab
2. Type your question in the text input at the bottom
3. Click "Send" or press Enter
4. The system will:
   - Search for relevant document chunks using semantic similarity
   - Generate an answer using the retrieved context
   - Display sources with similarity scores

### 3. Generate Summaries

1. Navigate to the **"Summarize"** tab
2. Select summary type (comprehensive, brief, or detailed)
3. Click "Generate Summary"
4. View the generated summary across all documents

## 🔧 How RAG Works

The RAG (Retrieval-Augmented Generation) pipeline works as follows:

1. **Document Processing**:
   - Text is extracted from uploaded documents
   - Text is split into overlapping chunks (512 characters with 50 character overlap)
   - Each chunk is embedded using SentenceTransformers (`all-MiniLM-L6-v2`)

2. **Vector Storage**:
   - Embeddings are stored in a FAISS index for fast similarity search
   - Metadata (filename, chunk index, text) is stored alongside embeddings

3. **Query Processing**:
   - User query is embedded using the same model
   - FAISS searches for top-k most similar chunks (default: 3)
   - Retrieved chunks are filtered by similarity threshold (0.7)

4. **Answer Generation**:
   - Retrieved context chunks are passed to the LLM along with the query
   - LLM generates an answer based on the provided context
   - Answer is returned with source citations

## 🎨 UI Design

The interface features:
- **Clean, minimal design** with neutral colors
- **Modern chat interface** with message bubbles
- **Source citations** showing document names and similarity scores
- **Real-time status** in the sidebar
- **Responsive layout** for different screen sizes

## 📊 System Status

The sidebar displays:
- Total number of documents processed
- Total number of chunks in the vector store
- System status (Ready/Not initialized/Error)
- LLM provider selection

## 🔍 Technical Details

### Embeddings
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimension**: 384
- **Normalization**: L2 normalization for cosine similarity

### Vector Store
- **Technology**: FAISS (Facebook AI Similarity Search)
- **Index Type**: IndexFlatL2 (Euclidean distance with L2 normalization)
- **Persistence**: Index and metadata saved to disk

### Chunking Strategy
- **Chunk Size**: 512 characters
- **Overlap**: 50 characters
- **Boundary Detection**: Attempts to break at sentence boundaries

### LLM Configuration
- **Gemini Model**: `gemini-pro` (default)
- **OpenAI Model**: `gpt-3.5-turbo`
- **HuggingFace Model**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Max Tokens**: 1000
- **Temperature**: 0.7

## 🛠️ Troubleshooting

### "Gemini API key not found"
- Ensure you have created a `.env` file with your Gemini API key: `GEMINI_API_KEY=your_key_here`
- Check that `python-dotenv` is installed
- Verify the API key is correct
- Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### "OpenAI API key not found" (if using OpenAI)
- Ensure you have created a `.env` file with your API key
- Check that `python-dotenv` is installed
- Verify the API key is correct

### "Error loading embedding model"
- Ensure you have internet connection (first-time download)
- Check that `sentence-transformers` is properly installed

### "No documents found"
- Make sure you've uploaded and processed at least one document
- Check the `data/documents/` directory for uploaded files

### Vector Store Issues
- If the vector store becomes corrupted, delete files in `data/vector_store/`
- The system will recreate the index on next document upload

## 📝 File Formats Supported

- **PDF**: `.pdf` files (using pypdf)
- **DOCX**: `.docx` files (using python-docx)
- **TXT**: `.txt` files (UTF-8 encoding)

## 🔐 Security Notes

- API keys are stored in `.env` file (not committed to version control)
- Documents are stored locally in `data/documents/`
- No data is sent to external services except for LLM API calls

## 🚧 Future Enhancements

Potential improvements:
- Support for more file formats (Excel, PowerPoint, etc.)
- Advanced chunking strategies (semantic chunking)
- Multi-modal support (images, tables)
- User authentication and document management
- Export chat history
- Batch document processing

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 👥 Credits

Built as a capstone project demonstrating end-to-end RAG implementation with modern tools and best practices.

---

**Note**: Make sure to add `.env` to your `.gitignore` file to keep your API keys secure!

