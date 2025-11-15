# How to Run the Document Knowledge Assistant

## Quick Start Guide

### Prerequisites Check
- ✅ Python 3.8+ installed
- ✅ Node.js 16+ and npm installed
- ✅ Gemini API key (get from https://makersuite.google.com/app/apikey)

---

## Step-by-Step Instructions

### Step 1: Install Python Dependencies

Open PowerShell/Terminal in the `Capstone_project` directory:

```powershell
cd Capstone_project
pip install -r requirements.txt
```

This installs:
- Flask (API server)
- Flask-CORS (for React frontend)
- All RAG pipeline dependencies

---

### Step 2: Configure API Key

Create a `.env` file in the `Capstone_project` folder:

**Windows (PowerShell):**
```powershell
cd Capstone_project
New-Item -ItemType File -Path .env
notepad .env
```

**Or manually create `.env` file with:**
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace `your_gemini_api_key_here` with your actual Gemini API key.

---

### Step 3: Install React Dependencies

Open a new terminal window:

```powershell
cd Capstone_project\frontend_react
npm install
```

This will install all React/TypeScript dependencies (first time may take a few minutes).

---

### Step 4: Start the Flask API Backend

**Terminal 1** - Keep this running:

```powershell
cd Capstone_project
python backend\api.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**OR use the batch file:**
```powershell
.\run_api.bat
```

---

### Step 5: Start the React Frontend

**Terminal 2** - Open a NEW terminal window:

```powershell
cd Capstone_project\frontend_react
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

---

### Step 6: Open the Application

1. Open your web browser
2. Go to: **http://localhost:3000**
3. You should see the Document Q&A interface

---

## Using the Application

### Upload a Document
1. Click "Upload a document" or drag & drop a file
2. Supported formats: PDF, DOCX, TXT
3. Wait for processing (you'll see "Processing document...")
4. Once processed, you'll see the document name

### Ask Questions
1. Type your question in the text area
2. Click "Ask Question"
3. The answer will appear with source citations

### Upload New Document
- Click the X button next to the document name to upload a new one

---

## Troubleshooting

### ❌ "Module not found" error when starting Flask API

**Solution:**
```powershell
pip install -r requirements.txt
```

### ❌ "npm: command not found"

**Solution:**
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

### ❌ "Failed to connect to API server" in browser

**Solution:**
1. Make sure Flask API is running (Terminal 1)
2. Check it's running on `http://localhost:5000`
3. Try accessing `http://localhost:5000/api/health` in browser - should return `{"status":"ok"}`

### ❌ "Gemini API key not found"

**Solution:**
1. Create `.env` file in `Capstone_project` folder
2. Add: `GEMINI_API_KEY=your_actual_key_here`
3. Restart the Flask API

### ❌ Port 5000 or 3000 already in use

**Solution for Flask (port 5000):**
- Edit `backend/api.py`, change `port=5000` to `port=5001`
- Update `frontend_react/vite.config.ts` proxy target to `http://localhost:5001`

**Solution for React (port 3000):**
- Edit `frontend_react/vite.config.ts`, change `port: 3000` to `port: 3001`

### ❌ CORS errors in browser console

**Solution:**
```powershell
pip install flask-cors
```

---

## Alternative: Run Streamlit UI Instead

If you prefer the Streamlit interface:

```powershell
cd Capstone_project
streamlit run frontend\app.py
```

Then open: `http://localhost:8501`

---

## Quick Commands Reference

### Start Backend (Flask API)
```powershell
cd Capstone_project
python backend\api.py
```

### Start Frontend (React)
```powershell
cd Capstone_project\frontend_react
npm run dev
```

### Check if API is running
Open browser: `http://localhost:5000/api/health`

### Check if React is running
Open browser: `http://localhost:3000`

---

## Project Structure

```
Capstone_project/
├── backend/
│   ├── api.py              # Flask API server (START THIS FIRST)
│   ├── rag_pipeline.py     # RAG processing
│   └── ...
├── frontend_react/         # React UI (START THIS SECOND)
│   ├── src/
│   └── package.json
├── .env                    # Your API keys (CREATE THIS)
└── requirements.txt        # Python dependencies
```

---

## Need Help?

1. Check that both terminals are running (Flask API + React)
2. Verify `.env` file exists with your Gemini API key
3. Check browser console for errors (F12)
4. Make sure ports 5000 and 3000 are not blocked by firewall

---

**Happy Document Q&A! 📚**

