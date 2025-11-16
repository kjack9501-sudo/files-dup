<#
run_all.ps1

Starts the backend (Flask) and frontend (React Vite) in two separate PowerShell windows.

Usage:
  .\run_all.ps1                 # Start Flask backend + React (npm run dev)
  .\run_all.ps1 -UseStreamlit  # Start Flask backend + Streamlit UI instead of React

Notes:
- If a virtual environment exists in `.venv`, `venv`, or `env`, the script will attempt to activate it in each window.
- Make sure Node.js/npm are installed for the React frontend.
#>

param(
    [switch]$UseStreamlit
)

# Resolve the script/project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Project root: $scriptDir"

# Find an activation script for common venv names
$possibleVenvs = @('.venv','venv','env')
$activatePath = $null
foreach ($v in $possibleVenvs) {
    $p = Join-Path $scriptDir "$v\Scripts\Activate.ps1"
    if (Test-Path $p) { $activatePath = $p; break }
}

if ($activatePath) { Write-Host "Found venv activation at: $activatePath" } else { Write-Host "No virtual environment activation script found. Skipping venv activation." }

# Build and launch backend window
$backendCmd = "cd `"$scriptDir`"; "
if ($activatePath) { $backendCmd += ". `"$activatePath`"; " }
$backendCmd += "python .\backend\api.py"

Write-Host "Launching backend..."
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$backendCmd -WindowStyle Normal

# Build and launch frontend window (React dev or Streamlit)
if ($UseStreamlit) {
    $frontendCmd = "cd `"$scriptDir`"; "
    if ($activatePath) { $frontendCmd += ". `"$activatePath`"; " }
    $frontendCmd += "streamlit run .\frontend\app.py"
    Write-Host "Launching Streamlit frontend..."
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$frontendCmd -WindowStyle Normal
} else {
    $frontendDir = Join-Path $scriptDir 'frontend_react'
    $frontendCmd = "cd `"$frontendDir`"; npm run dev"
    Write-Host "Launching React (Vite) frontend..."
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command",$frontendCmd -WindowStyle Normal
}

Write-Host "Done. Two windows should be open: backend and frontend."
