"""
SmartIDE - Application Entry Point
Initializes Qt application, configures themes and settings, and launches MainWindow.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.main_window import MainWindow
from app.styles import DarkTheme
from app.settings import SettingsManager
from utils.constants import APP_NAME, APP_VERSION
from utils.logger import get_logger

logger = get_logger("SmartIDE")


def parse_args():
    parser = argparse.ArgumentParser(description=f"{APP_NAME} v{APP_VERSION} - Desktop Python IDE")
    parser.add_argument("path", nargs="?", default=None, help="Initial project folder or file to open")
    parser.add_argument("--reset-project", action="store_true", help="Clear remembered project folder")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger.info("Starting %s v%s", APP_NAME, APP_VERSION)

    # Initialize Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Apply dark theme
    app.setStyleSheet(DarkTheme.get_stylesheet())

    # Handle --reset-project
    if args.reset_project:
        settings = SettingsManager()
        settings.clear_last_project()
        logger.info("Cleared last opened project path from settings.")

    # Determine initial directory
    initial_path = args.path
    if initial_path:
        initial_path = str(Path(initial_path).resolve())

    # Launch Main Window
    window = MainWindow(initial_path=initial_path)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
