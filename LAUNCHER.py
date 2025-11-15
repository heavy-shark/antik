"""
🤖 BOTASAURUS DESKTOP APP LAUNCHER 🤖

Simple launcher script for the Botasaurus Desktop Application.
Run this file to open the app!
"""

import sys
import os
from pathlib import Path

# CRITICAL: Remove local botasaurus source folder from path
# We want to use INSTALLED packages only, not local source code
antik_dir = Path(__file__).parent
local_botasaurus = str(antik_dir / "botasaurus")

# Filter out any paths that contain the local botasaurus folder
sys.path = [p for p in sys.path if local_botasaurus not in p and str(antik_dir) not in p]

# Add ONLY the botasaurus_app to path
app_dir = antik_dir / "botasaurus_app"
sys.path.insert(0, str(app_dir))

# Change to app directory (but don't add antik to path)
os.chdir(str(app_dir))

# Import and run
from app import main

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Starting Botasaurus Desktop App...")
    print("=" * 60)
    print()
    print("✅ No localhost required!")
    print("✅ Standalone desktop application")
    print("✅ Full browser profile management")
    print()
    print("=" * 60)

    main()
