"""Main application window for SmartIDE."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMenuBar,
    QMenu,
    QToolBar,
    QStatusBar,
    QDockWidget,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QFrame,
)
from PySide6.QtGui import QAction, QKeySequence

from utils.constants import APP_NAME, APP_VERSION
from utils.logger import get_logger
from app.settings import SettingsManager
from explorer.file_explorer import FileExplorerWidget

logger = get_logger("main_window")


class MainWindow(QMainWindow):
    """Main Application Window for SmartIDE."""

    def __init__(self, initial_project: Optional[Path] = None):
        super().__init__()
        self.settings = SettingsManager()
        self.current_project_path: Optional[Path] = None

        self._setup_window_properties()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_docks()
        self._create_central_widget()
        self._restore_state(initial_project)

        logger.info("MainWindow initialized successfully.")

    def _setup_window_properties(self) -> None:
        """Set up window title and minimum size."""
        self.setWindowTitle(f"{APP_NAME} - Professional Python IDE")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

    def _create_actions(self) -> None:
        """Create QActions for menus, toolbar, and shortcuts."""
        # File Actions
        self.action_new_file = QAction("New File", self)
        self.action_new_file.setShortcut(QKeySequence("Ctrl+N"))
        self.action_new_file.setStatusTip("Create a new file (Ctrl+N)")
        self.action_new_file.triggered.connect(self._on_action_not_implemented)

        self.action_open_file = QAction("Open File...", self)
        self.action_open_file.setShortcut(QKeySequence("Ctrl+O"))
        self.action_open_file.setStatusTip("Open an existing file (Ctrl+O)")
        self.action_open_file.triggered.connect(self._on_action_not_implemented)

        self.action_save = QAction("Save", self)
        self.action_save.setShortcut(QKeySequence("Ctrl+S"))
        self.action_save.setStatusTip("Save the active file (Ctrl+S)")
        self.action_save.triggered.connect(self._on_action_not_implemented)

        self.action_save_as = QAction("Save As...", self)
        self.action_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.action_save_as.setStatusTip("Save the active file under a new name")
        self.action_save_as.triggered.connect(self._on_action_not_implemented)

        self.action_close_file = QAction("Close", self)
        self.action_close_file.setShortcut(QKeySequence("Ctrl+W"))
        self.action_close_file.setStatusTip("Close the current file")
        self.action_close_file.triggered.connect(self._on_action_not_implemented)

        self.action_exit = QAction("Exit", self)
        self.action_exit.setShortcut(QKeySequence("Ctrl+Q"))
        self.action_exit.setStatusTip("Exit SmartIDE")
        self.action_exit.triggered.connect(self.close)

        # Edit Actions
        self.action_undo = QAction("Undo", self)
        self.action_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.action_undo.setStatusTip("Undo previous action")

        self.action_redo = QAction("Redo", self)
        self.action_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.action_redo.setStatusTip("Redo previous action")

        self.action_cut = QAction("Cut", self)
        self.action_cut.setShortcut(QKeySequence.StandardKey.Cut)
        self.action_cut.setStatusTip("Cut selected text")

        self.action_copy = QAction("Copy", self)
        self.action_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.action_copy.setStatusTip("Copy selected text")

        self.action_paste = QAction("Paste", self)
        self.action_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.action_paste.setStatusTip("Paste text from clipboard")

        self.action_find = QAction("Find...", self)
        self.action_find.setShortcut(QKeySequence.StandardKey.Find)
        self.action_find.setStatusTip("Find text in current file")

        self.action_replace = QAction("Replace...", self)
        self.action_replace.setShortcut(QKeySequence.StandardKey.Replace)
        self.action_replace.setStatusTip("Replace text in current file")
        self.action_open_folder = QAction("Open Folder...", self)
        self.action_open_folder.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.action_open_folder.setStatusTip("Open a project folder")
        self.action_open_folder.triggered.connect(self.open_project_folder_dialog)
        self.action_refresh_project = QAction("Refresh Project", self)
        self.action_refresh_project.setShortcut(QKeySequence("F5"))
        self.action_refresh_project.setStatusTip("Refresh project file tree (F5)")
        self.action_refresh_project.triggered.connect(self.refresh_project)

        # Database Actions (Phase 4)
        self.action_new_db = QAction("New SQLite Database...", self)
        self.action_new_db.setStatusTip("Create a new SQLite database (Phase 4)")
        self.action_new_db.triggered.connect(self._on_action_not_implemented)

        self.action_open_db = QAction("Open SQLite Database...", self)
        self.action_open_db.setStatusTip("Open an existing SQLite database (Phase 4)")
        self.action_open_db.triggered.connect(self._on_action_not_implemented)

        self.action_close_db = QAction("Close Database", self)
        self.action_close_db.setStatusTip("Close active database connection")
        self.action_close_db.triggered.connect(self._on_action_not_implemented)

        # Help Actions
        self.action_about = QAction("About SmartIDE", self)
        self.action_about.setStatusTip("About SmartIDE")
        self.action_about.triggered.connect(self.show_about_dialog)

def _create_menus(self) -> None:
        """Create menu bar and hierarchical menus."""
        menu_bar = self.menuBar()

        # File Menu
        self.menu_file = menu_bar.addMenu("&File")
        self.menu_file.addAction(self.action_new_file)
        self.menu_file.addAction(self.action_open_file)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_close_file)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)

        # Edit Menu
        self.menu_edit = menu_bar.addMenu("&Edit")
        self.menu_edit.addAction(self.action_undo)
        self.menu_edit.addAction(self.action_redo)
        self.menu_edit.addSeparator()
        self.menu_edit.addAction(self.action_cut)
        self.menu_edit.addAction(self.action_copy)
        self.menu_edit.addAction(self.action_paste)
        self.menu_edit.addSeparator()
        self.menu_edit.addAction(self.action_find)
        self.menu_edit.addAction(self.action_replace)

        # View Menu
        self.menu_view = menu_bar.addMenu("&View")
        # Toggle actions will be added when docks are created

        # Project Menu
        self.menu_project = menu_bar.addMenu("&Project")
        self.menu_project.addAction(self.action_open_folder)
        self.menu_project.addAction(self.action_refresh_project)

        # Database Menu
        self.menu_database = menu_bar.addMenu("&Database")
        self.menu_database.addAction(self.action_new_db)
        self.menu_database.addAction(self.action_open_db)
        self.menu_database.addAction(self.action_close_db)

        # Help Menu
        self.menu_help = menu_bar.addMenu("&Help")
        self.menu_help.addAction(self.action_about)

def _create_toolbars(self) -> None:
        """Create main toolbar with essential quick actions."""
        self.main_toolbar = QToolBar("Main Toolbar", self)
        self.main_toolbar.setMovable(False)
        self.main_toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        # Project actions
        self.main_toolbar.addAction(self.action_open_folder)
        self.main_toolbar.addAction(self.action_refresh_project)
        self.main_toolbar.addSeparator()

        # File actions
        self.main_toolbar.addAction(self.action_new_file)
        self.main_toolbar.addAction(self.action_open_file)
        self.main_toolbar.addAction(self.action_save)

def _create_status_bar(self) -> None:
        """Create status bar with status message and info widgets."""
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Left status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, stretch=1)

        # Right status widgets
        self.project_status_label = QLabel("No Project")
        self.project_status_label.setStyleSheet("color: #ffffff; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.project_status_label)

        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setStyleSheet("color: #ffffff; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.encoding_label)

        self.cursor_label = QLabel("Ln 1, Col 1")
        self.cursor_label.setStyleSheet("color: #ffffff; padding: 0 8px;")
        self.status_bar.addPermanentWidget(self.cursor_label)

        self.lang_label = QLabel("Python")
        self.lang_label.setStyleSheet("color: #ffffff; padding: 0 8px; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.lang_label)

def _create_docks(self) -> None:
        """Create left and right dock widgets."""
        # 1. Left Dock: File Explorer
        self.explorer_dock = QDockWidget("File Explorer", self)
        self.explorer_dock.setObjectName("FileExplorerDock")
        self.explorer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.file_explorer = FileExplorerWidget(self.explorer_dock)
        self.file_explorer.file_double_clicked.connect(self._on_file_double_clicked)
        self.file_explorer.file_selected.connect(self._on_file_selected)
        self.file_explorer.project_opened.connect(self._on_project_opened)

        self.explorer_dock.setWidget(self.file_explorer)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorer_dock)

        # 2. Right Dock: Database Explorer (Phase 4 placeholder)
        self.database_dock = QDockWidget("Database Explorer", self)
        self.database_dock.setObjectName("DatabaseExplorerDock")
        self.database_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        db_placeholder = QWidget()
        db_layout = QVBoxLayout(db_placeholder)
        db_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        db_title = QLabel("DATABASE EXPLORER")
        db_title.setStyleSheet("font-weight: 600; color: #888888; font-size: 12px;")
        db_desc = QLabel("SQLite database connection &\nCRUD tools will be enabled in Phase 4.")
        db_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        db_desc.setStyleSheet("color: #666666; font-size: 11px;")
        db_layout.addWidget(db_title)
        db_layout.addWidget(db_desc)
        self.database_dock.setWidget(db_placeholder)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.database_dock)
        # Keep database dock collapsed/hidden initially until needed
        self.database_dock.hide()

        # Add toggle actions to View Menu
        self.menu_view.addAction(self.explorer_dock.toggleViewAction())
        self.menu_view.addAction(self.database_dock.toggleViewAction())
        self.menu_view.addSeparator()

        action_toggle_status_bar = self.status_bar.toggleViewAction() if hasattr(self.status_bar, "toggleViewAction") else None
        if not action_toggle_status_bar:
            action_toggle_status_bar = QAction("Status Bar", self, checkable=True)
            action_toggle_status_bar.setChecked(True)
            action_toggle_status_bar.toggled.connect(self.status_bar.setVisible)
        self.menu_view.addAction(action_toggle_status_bar)

def _create_central_widget(self) -> None:
        """Create central widget area with welcoming placeholder for Phase 1."""
        self.central_container = QWidget(self)
        layout = QVBoxLayout(self.central_container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title_label = QLabel(f"Welcome to {APP_NAME}")
        title_label.setStyleSheet("font-size: 26px; font-weight: 700; color: #ffffff;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        sub_label = QLabel(f"Modular Python IDE MVP (v{APP_VERSION}) — Phase 1 Shell")
        sub_label.setStyleSheet("font-size: 14px; color: #888888;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_label)

        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #252526; border: 1px solid #333333; border-radius: 8px; padding: 24px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        prompt_label = QLabel("Get Started:")
        prompt_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #007acc;")
        card_layout.addWidget(prompt_label)

        btn_open = QPushButton("Open Project Folder  (Ctrl+Shift+O)")
        btn_open.clicked.connect(self.open_project_folder_dialog)
        card_layout.addWidget(btn_open)

        info_label = QLabel(
            "• Use the File Explorer on the left to browse project files.\n"
            "• Phase 2 will introduce the QScintilla code editor with tabs and Python syntax highlighting."
        )
        info_label.setStyleSheet("color: #aaaaaa; font-size: 12px; line-height: 1.5;")
        card_layout.addWidget(info_label)

        layout.addWidget(card)
        self.setCentralWidget(self.central_container)

def open_project_folder_dialog(self) -> None:
        """Show directory picker dialog to open a project folder."""
        initial_dir = str(self.current_project_path) if self.current_project_path else str(Path.cwd())
        chosen_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            initial_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if chosen_dir:
            self.set_project_path(Path(chosen_dir))

def set_project_path(self, path: Path | str) -> bool:
        """Set project path in window, file explorer, and settings."""
        p = Path(path).resolve()
        if not p.is_dir():
            QMessageBox.critical(self, "Error", f"Invalid project folder:\n{p}")
            return False

        self.current_project_path = p
        self.file_explorer.set_project_path(p)
        self.setWindowTitle(f"{APP_NAME} - {p.name} [{p}]")
        self.project_status_label.setText(f"Project: {p.name}")
        self.status_label.setText(f"Opened project: {p}")
        self.settings.set_last_project(p)
        logger.info("Project set to: %s", p)
        return True

def refresh_project(self) -> None:
        """Refresh current project tree view."""
        self.file_explorer.refresh()
        self.status_label.setText("Project explorer refreshed.")

def show_about_dialog(self) -> None:
        """Show About dialog."""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            f"<p>A clean, modular Python IDE MVP built with PySide6 and SQLite3.</p>"
            f"<p><b>Phase 1 Completed:</b></p>"
            f"<ul>"
            f"<li>Application Shell & Dark Theme</li>"
            f"<li>File Explorer with Qt Model/View Architecture</li>"
            f"<li>Project Folder Management</li>"
            f"<li>Menu Bar, Toolbars, and Status Bar</li>"
            f"<li>Dockable Panel Architecture</li>"
            f"</ul>"
            f"<p>Designed for industrial modularity and future extensibility.</p>",
        )

def _on_file_double_clicked(self, file_path: Path) -> None:
        """Handle file double clicked in file explorer."""
        self.status_label.setText(f"Selected: {file_path.name}")
        logger.info("File selected for opening in Phase 2: %s", file_path)

def _on_file_selected(self, file_path: Path) -> None:
        """Handle single click in file explorer."""
        self.status_label.setText(str(file_path))

def _on_project_opened(self, project_path: Path) -> None:
        """Handle project opened signal from explorer."""
        self.current_project_path = project_path
        self.setWindowTitle(f"{APP_NAME} - {project_path.name}")
        self.project_status_label.setText(f"Project: {project_path.name}")

def _on_action_not_implemented(self) -> None:
        """Notify user that feature will be enabled in subsequent phase."""
        sender = self.sender()
        action_name = sender.text() if sender else "Action"
        QMessageBox.information(
            self,
            "Feature in Next Phase",
            f"'{action_name}' is scheduled for implementation in Phase 2 (Code Editor & Tabs).",
        )

def _restore_state(self, initial_project: Optional[Path] = None) -> None:
        """Restore window geometry and project from settings or CLI arguments."""
        geom = self.settings.get_window_geometry()
        if geom:
            self.restoreGeometry(geom)

        state = self.settings.get_window_state()
        if state:
            self.restoreState(state)

        # Restore project
        target_project = initial_project or self.settings.get_last_project() or Path.cwd()
        if target_project and target_project.is_dir():
            self.set_project_path(target_project)

def closeEvent(self, event) -> None:
        """Save settings and geometry on application close."""
        self.settings.set_window_geometry(self.saveGeometry())
        self.settings.set_window_state(self.saveState())
        logger.info("MainWindow closing, geometry and state persisted.")
        super().closeEvent(event)
