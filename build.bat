@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building exe...
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name VoiceInput ^
  --add-data "web;web" ^
  server.py

echo.
echo Done! Find VoiceInput.exe in the dist\ folder.
pause
