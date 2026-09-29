"""Application-wide constants for SmartIDE."""
from pathlib import Path

# Application Metadata
APP_NAME = "SmartIDE"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "SmartIDE Team"
APP_DOMAIN = "smartide.local"

# File extensions & types
SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".sql": "SQL",
    ".json": "JSON",
    ".txt": "Plain Text",
    ".md": "Markdown",
    ".db": "SQLite Database",
    ".sqlite": "SQLite Database",
    ".sqlite3": "SQLite Database",
}

# Settings Keys
SETTING_LAST_PROJECT = "general/last_project"
SETTING_GEOMETRY = "window/geometry"
SETTING_WINDOW_STATE = "window/state"
SETTING_THEME = "appearance/theme"
SETTING_RECENT_PROJECTS = "general/recent_projects"

# Directory & Log Paths
APP_DATA_DIR = Path.home() / ".smartide"
LOG_FILE_PATH = APP_DATA_DIR / "smartide.log"
