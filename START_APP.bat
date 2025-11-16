@echo off
echo ========================================
echo  Hysk Mexc Futures v0.2
echo  Starting with CONSOLE window...
echo ========================================
echo.
echo NOTE: For silent start (no console),
echo       use START_APP_SILENT.bat or
echo       double-click launcher.pyw
echo.

cd /d "%~dp0"
"C:\Users\daniel\AppData\Local\Programs\Python\Python312\python.exe" botasaurus_app\app.py

pause
