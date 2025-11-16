"""
Flask API backend for the RAG Document Knowledge Assistant.
Provides REST endpoints for document upload, processing, and question answering.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import sys

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.rag_pipeline import RAGPipeline
from backend.config import DOCUMENTS_DIR, DEFAULT_LLM_PROVIDER

app = Flask(__name__)

# Configure CORS with more permissive settings
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True)

# Initialize RAG pipeline
rag_pipeline = None

def get_rag_pipeline():
    """Get or initialize RAG pipeline with Gemini."""
    global rag_pipeline
    if rag_pipeline is None:
        rag_pipeline = RAGPipeline(llm_provider=DEFAULT_LLM_PROVIDER)
    return rag_pipeline


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "message": "Document Knowledge Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload (POST)",
            "ask": "/api/ask (POST)",
            "summary": "/api/summary (POST)",
            "statistics": "/api/statistics (GET)"
        }
    }), 200


@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint."""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    return jsonify({"status": "ok", "message": "API is running"})


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload and process a document."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save file
        filename = file.filename
        file_path = DOCUMENTS_DIR / filename
        
        # Handle duplicate filenames
        counter = 1
        original_path = file_path
        while file_path.exists():
            name_parts = original_path.stem, original_path.suffix
            file_path = DOCUMENTS_DIR / f"{name_parts[0]}_{counter}{name_parts[1]}"
            counter += 1
        
        file.save(str(file_path))
        
        # Process document
        pipeline = get_rag_pipeline()
        result = pipeline.process_document(str(file_path))
        
        if result["success"]:
            return jsonify({
                "success": True,
                "documentId": f"doc_{Path(file_path).stem}",
                "filename": result["filename"],
                "chunksCount": result["chunks_count"],
                "message": f"Document processed successfully with {result['chunks_count']} chunks"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error")
            }), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Ask a question about the documents."""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "Question is required"}), 400
        
        pipeline = get_rag_pipeline()
        result = pipeline.answer_question(question)
        
        # Ensure all sources have JSON-serializable values
        sources = result.get("sources", [])
        serializable_sources = []
        for source in sources:
            serializable_source = {
                "filename": str(source.get("filename", "")),
                "chunk_index": int(source.get("chunk_index", 0)),
                "similarity": float(source.get("similarity", 0.0))
            }
            serializable_sources.append(serializable_source)
        
        return jsonify({
            "success": True,
            "answer": str(result["answer"]),
            "sources": serializable_sources,
            "contextUsed": bool(result.get("context_used", False))
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/summary', methods=['POST'])
def generate_summary():
    """Generate a summary of all documents."""
    try:
        data = request.get_json()
        summary_type = data.get('type', 'comprehensive')
        
        pipeline = get_rag_pipeline()
        result = pipeline.generate_multi_document_summary(summary_type)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "summary": result["summary"],
                "documentCount": result["document_count"],
                "totalChunks": result["total_chunks"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error")
            }), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get system statistics."""
    try:
        pipeline = get_rag_pipeline()
        stats = pipeline.get_statistics()
        
        return jsonify({
            "success": True,
            "totalDocuments": stats["documents"],
            "totalChunks": stats["total_vectors"],
            "embeddingDimension": stats["embedding_dimension"]
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "The requested URL was not found on the server.",
        "available_endpoints": [
            "GET /",
            "GET /api/health",
            "POST /api/upload",
            "POST /api/ask",
            "POST /api/summary",
            "GET /api/statistics"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": str(error) if app.debug else "An internal error occurred"
    }), 500


if __name__ == '__main__':
    # Run Flask server
    print("=" * 50)
    print("Document Knowledge Assistant API")
    print("=" * 50)
    print("Starting server on http://localhost:8000")
    print("Available endpoints:")
    print("  GET  /              - API information")
    print("  GET  /api/health    - Health check")
    print("  POST /api/upload    - Upload document")
    print("  POST /api/ask       - Ask question")
    print("  POST /api/summary   - Generate summary")
    print("  GET  /api/statistics - Get statistics")
    print("=" * 50)
    print()
    app.run(host='0.0.0.0', port=8000, debug=True)

