# Quick Start Guide

## 🚀 Running the Application (Windows)

### Step 1: Navigate to Project Directory
```powershell
cd Capstone_project
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment
```powershell
venv\Scripts\activate
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Create .env File
Create a file named `.env` in the `Capstone_project` folder with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note:** Gemini is the default. You can also add OpenAI or HuggingFace keys if you want to switch providers.

### Step 6: Run the Application
```powershell
streamlit run frontend/app.py
```

**OR** simply double-click `run_app.bat`

---

## 📝 Alternative: Run Without Virtual Environment

If you prefer not to use a virtual environment:

1. Open PowerShell in the `Capstone_project` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your API key
4. Run: `streamlit run frontend/app.py`

---

## ⚠️ Troubleshooting

**Issue: "Module not found"**
- Make sure you're in the `Capstone_project` directory
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Issue: "API key not found"**
- Create a `.env` file in `Capstone_project` folder
- Add your Gemini API key: `GEMINI_API_KEY=your_key_here`
- Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Issue: "Port already in use"**
- Streamlit will automatically try another port
- Or specify a port: `streamlit run frontend/app.py --server.port 8502`

---

## 🎯 First Steps After Launching

1. **Upload Documents**: Go to "Upload Documents" tab → Upload PDF/DOCX/TXT → Click "Process"
2. **Ask Questions**: Go to "Chat" tab → Type your question → Click "Send"
3. **Generate Summary**: Go to "Summarize" tab → Click "Generate Summary"

