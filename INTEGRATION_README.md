# Integration Guide: React UI with RAG Backend

This guide explains how to run the complete system with the React frontend and Flask API backend.

## Architecture

```
Capstone_project/
├── backend/
│   ├── api.py          # Flask API server
│   ├── rag_pipeline.py # RAG pipeline
│   └── ...
├── frontend_react/     # React/TypeScript UI
│   └── ...
└── frontend/           # Streamlit UI (alternative)
```

## Quick Start

### 1. Start the Flask API Backend

**Windows:**
```powershell
cd Capstone_project
.\run_api.bat
```

**Linux/Mac:**
```bash
cd Capstone_project
chmod +x run_api.sh
./run_api.sh
```

**Or manually:**
```bash
cd Capstone_project/backend
python api.py
```

The API will run on `http://localhost:5000`

### 2. Start the React Frontend

Open a new terminal:

```bash
cd Capstone_project/frontend_react
npm install
npm run dev
```

The React app will run on `http://localhost:3000`

### 3. Access the Application

Open your browser and go to: `http://localhost:3000`

## Configuration

### Backend (.env file)

Create a `.env` file in `Capstone_project/`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Frontend (.env file)

Optionally create a `.env` file in `Capstone_project/frontend_react/`:

```
VITE_API_URL=http://localhost:5000
```

## API Endpoints

### POST /api/upload
Upload and process a document.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: `file` (PDF, DOCX, or TXT)

**Response:**
```json
{
  "success": true,
  "documentId": "doc_filename",
  "filename": "document.pdf",
  "chunksCount": 10,
  "message": "Document processed successfully with 10 chunks"
}
```

### POST /api/ask
Ask a question about uploaded documents.

**Request:**
```json
{
  "question": "What is the main topic of the document?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "The main topic is...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_index": 0,
      "similarity": 0.85
    }
  ],
  "contextUsed": true
}
```

### POST /api/summary
Generate a summary of all documents.

**Request:**
```json
{
  "type": "comprehensive"
}
```

**Response:**
```json
{
  "success": true,
  "summary": "Summary text...",
  "documentCount": 3,
  "totalChunks": 45
}
```

### GET /api/statistics
Get system statistics.

**Response:**
```json
{
  "success": true,
  "totalDocuments": 3,
  "totalChunks": 45,
  "embeddingDimension": 384
}
```

## Troubleshooting

### "Failed to connect to API server"
- Make sure the Flask API is running on port 5000
- Check that CORS is enabled in the Flask app
- Verify the API URL in the frontend `.env` file

### "Module not found" errors
- Run `npm install` in the `frontend_react` directory
- Make sure all Python dependencies are installed: `pip install -r requirements.txt`

### Port conflicts
- Change the Flask port in `backend/api.py`: `app.run(port=5001)`
- Change the React port in `frontend_react/vite.config.ts`: `server: { port: 3001 }`

## Development

### Backend Development
- The Flask API runs in debug mode by default
- Changes to Python files require restarting the server

### Frontend Development
- Vite provides hot module replacement (HMR)
- Changes to React files will automatically reload

## Production Deployment

### Build React App
```bash
cd frontend_react
npm run build
```

### Serve with Flask
You can serve the built React app from Flask by adding a route in `api.py`:

```python
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

Then copy the `dist` folder from React build to Flask's static folder.

