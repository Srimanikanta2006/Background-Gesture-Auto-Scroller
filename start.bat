@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\pythonw.exe" (
    echo [!] Virtual environment not found. Running setup.bat first...
    call setup.bat
)

echo [*] Starting Gesture Scroller in background...
start "" ".venv\Scripts\pythonw.exe" "main.pyw"
echo [+] Running! Look for the icon in your system tray (bottom-right near clock).
timeout /t 2 >nul
