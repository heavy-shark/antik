@echo off
REM ========================================
REM  Hysk Mexc Futures - Silent Launcher
REM  Starts app without console window
REM ========================================

cd /d "%~dp0"

REM Launch using pythonw.exe (no console window)
start "" "C:\Users\daniel\AppData\Local\Programs\Python\Python312\pythonw.exe" launcher.pyw

REM Exit immediately (don't wait)
exit
