"""
Hysk Mexc Futures - Silent Launcher (No Console Window)

This launcher file uses .pyw extension which runs with pythonw.exe
and doesn't show a console window.

Usage:
    Double-click this file to launch the app without console
    OR
    python launcher.pyw
"""
import sys
import os
from pathlib import Path

# Set up path to botasaurus_app
app_dir = Path(__file__).parent / "botasaurus_app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Change to app directory
os.chdir(str(app_dir))

# Import and run the app
from app import main

if __name__ == "__main__":
    main()
