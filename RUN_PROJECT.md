# How to Run the Project

## Quick Start

### Option 1: Use Batch Files (Windows)

**Terminal 1 - Start API:**
```batch
START_PROJECT.bat
```

**Terminal 2 - Start React:**
```batch
START_REACT.bat
```

### Option 2: Manual Commands

**Terminal 1 - Start Flask API:**
```powershell
cd Capstone_project
python backend\api.py
```

**Terminal 2 - Start React Frontend:**
```powershell
cd Capstone_project\frontend_react
npm install
npm run dev
```

## Prerequisites

1. **Create `.env` file** in `Capstone_project/` folder:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

2. **Install Python dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Install React dependencies** (first time only):
   ```powershell
   cd frontend_react
   npm install
   ```

## Access the Application

- **React UI**: http://localhost:3000
- **API Health Check**: http://localhost:5000/api/health

## Troubleshooting

### API not starting
- Check if `.env` file exists with `GEMINI_API_KEY`
- Make sure port 5000 is not in use
- Check Python dependencies: `pip install -r requirements.txt`

### React not starting
- Run `npm install` in `frontend_react` directory
- Check if Node.js is installed: `node --version`
- Make sure port 3000 is not in use

### Import errors
- Make sure you're in the `Capstone_project` directory
- Check that all Python packages are installed

