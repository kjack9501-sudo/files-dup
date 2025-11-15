# Quick Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 16+ and npm
- Gemini API key

## Step 1: Install Python Dependencies

```bash
cd Capstone_project
pip install -r requirements.txt
```

## Step 2: Configure API Key

Create `.env` file in `Capstone_project/`:
```
GEMINI_API_KEY=your_api_key_here
```

## Step 3: Install React Dependencies

```bash
cd Capstone_project/frontend_react
npm install
```

## Step 4: Run the System

### Terminal 1 - Start Flask API:
```bash
cd Capstone_project
python backend/api.py
```

### Terminal 2 - Start React Frontend:
```bash
cd Capstone_project/frontend_react
npm run dev
```

## Step 5: Access the Application

Open browser: `http://localhost:3000`

## Troubleshooting

- **API not responding**: Check Flask is running on port 5000
- **CORS errors**: Make sure flask-cors is installed
- **Module not found**: Run `npm install` in frontend_react directory

