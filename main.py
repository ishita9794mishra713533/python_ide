"""SmartIDE - Entry Point."""
import sys
import argparse
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from utils.logger import setup_logger, get_logger
from utils.constants import APP_NAME, APP_ORGANIZATION, APP_DOMAIN
from app.styles import apply_dark_theme
from app.main_window import MainWindow
from explorer.file_manager import FileManager


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - Modular Python Desktop IDE")
    parser.add_argument(
        "project_path",
        nargs="?",
        default=None,
        help="Optional path to a project folder to open on startup",
    )
    return parser.parse_args()


def validate_initial_project(project_path_arg: str | None) -> Path | None:
    """Validate initial project path given via command line using FileManager validation."""
    if not project_path_arg:
        return None
    candidate = Path(project_path_arg).resolve()
    if FileManager.is_valid_directory(candidate):
        return candidate
    return None


def main() -> int:
    """Main application lifecycle runner."""
    # 1. Setup centralized logging
    logger = setup_logger()
    logger.info("Starting %s application...", APP_NAME)

    # 2. Parse arguments and validate project path using FileManager
    args = parse_arguments()
    initial_project = validate_initial_project(args.project_path)

    if args.project_path and not initial_project:
        logger.warning("Provided CLI project path is invalid or non-existent: %s", args.project_path)
    elif initial_project:
        logger.info("Validated CLI project path: %s", initial_project)

    # 3. Create Qt Application
    # Enable High DPI scaling
    QApplication.setOrganizationName(APP_ORGANIZATION)
    QApplication.setOrganizationDomain(APP_DOMAIN)
    QApplication.setApplicationName(APP_NAME)

    app = QApplication(sys.argv)

    # 4. Apply Dark Professional Theme
    apply_dark_theme(app)

    # 5. Initialize Main Window
    window = MainWindow(initial_project=initial_project)
    window.show()

    logger.info("%s ready and event loop started.", APP_NAME)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


