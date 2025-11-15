"""
Quick test script to verify the app can launch
"""
import sys
from pathlib import Path

print("=" * 60)
print("Testing Botasaurus Desktop App Import...")
print("=" * 60)
print()

# Get directories
antik_dir = Path(__file__).parent
local_botasaurus = str(antik_dir / "botasaurus")

# Filter out local botasaurus
print(f"Removing local botasaurus from path: {local_botasaurus}")
sys.path = [p for p in sys.path if local_botasaurus not in p and str(antik_dir) not in p]

# Test imports
print("\n1. Testing botasaurus_driver import...")
try:
    from botasaurus_driver import Driver
    print("   ✅ botasaurus_driver imported successfully!")
except ImportError as e:
    print(f"   ❌ Failed to import botasaurus_driver: {e}")
    sys.exit(1)

print("\n2. Testing PySide6 import...")
try:
    from PySide6.QtWidgets import QApplication
    print("   ✅ PySide6 imported successfully!")
except ImportError as e:
    print(f"   ❌ Failed to import PySide6: {e}")
    sys.exit(1)

print("\n3. Testing app modules...")
app_dir = antik_dir / "botasaurus_app"
sys.path.insert(0, str(app_dir))

try:
    from profile_manager import ProfileManager
    print("   ✅ profile_manager imported successfully!")
except ImportError as e:
    print(f"   ❌ Failed to import profile_manager: {e}")
    sys.exit(1)

try:
    from scraper_runner import ScraperRunner
    print("   ✅ scraper_runner imported successfully!")
except ImportError as e:
    print(f"   ❌ Failed to import scraper_runner: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL IMPORTS SUCCESSFUL!")
print("=" * 60)
print()
print("The app is ready to launch!")
print("Run: START_APP.bat")
print()
