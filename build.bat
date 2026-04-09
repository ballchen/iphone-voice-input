@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building exe...
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name VoiceInput ^
  --collect-submodules engineio.async_drivers ^
  --hidden-import engineio.async_drivers.threading ^
  --add-data "web;web" ^
  server.py

echo.
echo Done! Find VoiceInput.exe in the dist\ folder.
pause
