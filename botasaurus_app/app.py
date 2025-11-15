"""
Botasaurus Desktop App - Main Launcher
A standalone desktop application for browser automation with profile management
"""
import sys
from pathlib import Path

# CRITICAL: Ensure we use INSTALLED packages, not local source
# Remove parent antik directory from path to avoid importing local botasaurus
app_dir = Path(__file__).parent
antik_dir = app_dir.parent
local_botasaurus = str(antik_dir / "botasaurus")

# Filter out local botasaurus from sys.path
sys.path = [p for p in sys.path if local_botasaurus not in p and str(antik_dir) not in p]
# Add back only the app directory
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from main_window import MainWindow


def main():
    """Main entry point for the application"""
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Botasaurus Desktop")
    app.setOrganizationName("Botasaurus")

    # Apply dark theme style (optional)
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
