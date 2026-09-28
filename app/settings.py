"""Application settings management."""
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QSettings, QByteArray
from utils.constants import (
    APP_NAME,
    APP_ORGANIZATION,
    SETTING_LAST_PROJECT,
    SETTING_GEOMETRY,
    SETTING_WINDOW_STATE,
    SETTING_THEME,
    SETTING_RECENT_PROJECTS,
)
from utils.logger import get_logger

logger = get_logger("settings")


class SettingsManager:
    """Manages application persistent configuration via QSettings."""

    def __init__(self):
        self._settings = QSettings(APP_ORGANIZATION, APP_NAME)

    def get_last_project(self) -> Optional[Path]:
        """Retrieve the last opened project directory path if valid."""
        path_str = self._settings.value(SETTING_LAST_PROJECT, defaultValue=None, type=str)
        if path_str:
            p = Path(path_str)
            if p.is_dir():
                return p
        return None

    def set_last_project(self, project_path: Optional[Path]) -> None:
        """Store the last opened project directory path and update recent projects."""
        if project_path is None:
            self._settings.remove(SETTING_LAST_PROJECT)
            return

        resolved = str(project_path.resolve())
        self._settings.setValue(SETTING_LAST_PROJECT, resolved)
        self.add_recent_project(project_path)

    def get_recent_projects(self) -> List[str]:
        """Return the list of recent project directory paths."""
        recents = self._settings.value(SETTING_RECENT_PROJECTS, defaultValue=[], type=list)
        return [str(p) for p in recents if Path(str(p)).is_dir()]

    def add_recent_project(self, project_path: Path) -> None:
        """Add a project to recent projects list, keeping up to 10 entries."""
        resolved = str(project_path.resolve())
        recents = self.get_recent_projects()
        if resolved in recents:
            recents.remove(resolved)
        recents.insert(0, resolved)
        self._settings.setValue(SETTING_RECENT_PROJECTS, recents[:10])

    def get_window_geometry(self) -> Optional[QByteArray]:
        """Return saved window geometry byte array."""
        val = self._settings.value(SETTING_GEOMETRY)
        if isinstance(val, QByteArray):
            return val
        return None

    def set_window_geometry(self, geometry: QByteArray) -> None:
        """Save window geometry."""
        self._settings.setValue(SETTING_GEOMETRY, geometry)

    def get_window_state(self) -> Optional[QByteArray]:
        """Return saved dock and toolbar state byte array."""
        val = self._settings.value(SETTING_WINDOW_STATE)
        if isinstance(val, QByteArray):
            return val
        return None

    def set_window_state(self, state: QByteArray) -> None:
        """Save dock and toolbar state."""
        self._settings.setValue(SETTING_WINDOW_STATE, state)

    def get_theme(self) -> str:
        """Get active theme name."""
        return self._settings.value(SETTING_THEME, defaultValue="dark", type=str)

    def set_theme(self, theme_name: str) -> None:
        """Set active theme name."""
        self._settings.setValue(SETTING_THEME, theme_name)
