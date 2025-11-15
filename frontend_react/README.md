# React Frontend for Document Knowledge Assistant

This is the React/TypeScript frontend for the RAG Document Knowledge Assistant.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional, defaults to `http://localhost:5000`):
```
VITE_API_URL=http://localhost:5000
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Features

- **Document Upload**: Drag and drop or click to upload PDF, DOCX, or TXT files
- **Question Answering**: Ask questions about uploaded documents
- **Source Citations**: View which document chunks were used to generate answers
- **Clean UI**: Minimal, modern design with Tailwind CSS

## API Endpoints

The frontend expects the Flask API to be running on `http://localhost:5000` (or the URL specified in `.env`):

- `POST /api/upload` - Upload and process a document
- `POST /api/ask` - Ask a question about documents
- `POST /api/summary` - Generate a summary (not yet implemented in UI)
- `GET /api/statistics` - Get system statistics (not yet implemented in UI)
- `GET /api/health` - Health check

