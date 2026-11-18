@echo off
rem Launch standalone Claude-Chan uniform build (port 47801, independent data dir)
cd /d "%~dp0"
start "" "%~dp0.venv\Scripts\pythonw.exe" -m claude_chan
