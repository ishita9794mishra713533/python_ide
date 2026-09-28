"""File explorer dock widget implementing Qt Model/View architecture."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QModelIndex, QDir
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeView,
    QFileSystemModel,
    QToolButton,
    QFileDialog,
    QMenu,
    QMessageBox,
)
from PySide6.QtGui import QAction, QIcon

from utils.logger import get_logger
from explorer.file_manager import FileManager

logger = get_logger("file_explorer")


class FileExplorerWidget(QWidget):
    """File Explorer panel showing project tree using QFileSystemModel."""

    # Signals
    file_double_clicked = Signal(Path)
    file_selected = Signal(Path)
    project_opened = Signal(Path)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project_path: Optional[Path] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header_widget = QWidget()
        header_widget.setObjectName("explorerHeader")
        header_widget.setStyleSheet(
            "QWidget#explorerHeader { background-color: #252526; border-bottom: 1px solid #333333; padding: 4px; }"
        )
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 4, 4)
        header_layout.setSpacing(4)

        self.project_title_label = QLabel("NO FOLDER OPENED")
        self.project_title_label.setStyleSheet("font-weight: 600; font-size: 11px; color: #bbbbbb;")
        header_layout.addWidget(self.project_title_label, stretch=1)

        # Header buttons
        self.btn_open = QToolButton()
        self.btn_open.setText("📁")
        self.btn_open.setToolTip("Open Folder")
        self.btn_open.clicked.connect(self._on_open_folder_clicked)
        header_layout.addWidget(self.btn_open)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setText("🔄")
        self.btn_refresh.setToolTip("Refresh Explorer")
        self.btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(self.btn_refresh)

        self.btn_collapse = QToolButton()
        self.btn_collapse.setText("➖")
        self.btn_collapse.setToolTip("Collapse All")
        self.btn_collapse.clicked.connect(self.collapse_all)
        header_layout.addWidget(self.btn_collapse)

        layout.addWidget(header_widget)

        # File system model
        self.fs_model = QFileSystemModel(self)
        self.fs_model.setReadOnly(False)
        self.fs_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        # Tree View
        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(16)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Hide Size, Type, Date Modified columns for clean IDE look
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        # Signals
        self.tree_view.doubleClicked.connect(self._on_tree_double_clicked)
        self.tree_view.clicked.connect(self._on_tree_clicked)
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.tree_view, stretch=1)

    def set_project_path(self, path: Path | str) -> bool:
        """Set root path of the file explorer."""
        p = Path(path).resolve()
        if not FileManager.is_valid_directory(p):
            logger.warning("Invalid directory provided to explorer: %s", path)
            return False

        self.project_path = p
        self.project_title_label.setText(p.name.upper())

        # Set root in model and tree view
        root_index = self.fs_model.setRootPath(str(p))
        self.tree_view.setRootIndex(root_index)

        logger.info("Project path set to: %s", p)
        self.project_opened.emit(p)
        return True

    def get_project_path(self) -> Optional[Path]:
        """Return the current project root path."""
        return self.project_path

    def refresh(self) -> None:
        """Refresh the filesystem model."""
        if self.project_path:
            logger.debug("Refreshing filesystem model for: %s", self.project_path)
            # Re-setting root path forces model refresh
            self.fs_model.setRootPath(str(self.project_path))
            root_idx = self.fs_model.index(str(self.project_path))
            self.tree_view.setRootIndex(root_idx)

    def collapse_all(self) -> None:
        """Collapse all expanded directories."""
        self.tree_view.collapseAll()

    def get_selected_path(self) -> Optional[Path]:
        """Get the filesystem Path of the currently selected item."""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return self.project_path
        index = indexes[0]
        file_path_str = self.fs_model.filePath(index)
        return Path(file_path_str) if file_path_str else self.project_path

    def _on_tree_double_clicked(self, index: QModelIndex) -> None:
        """Handle double click on tree item."""
        file_path_str = self.fs_model.filePath(index)
        if not file_path_str:
            return

        p = Path(file_path_str)
        if p.is_file():
            logger.info("File double clicked: %s", p)
            self.file_double_clicked.emit(p)

    def _on_tree_clicked(self, index: QModelIndex) -> None:
        """Handle single click on tree item for selection."""
        file_path_str = self.fs_model.filePath(index)
        if file_path_str:
            self.file_selected.emit(Path(file_path_str))

    def _on_open_folder_clicked(self) -> None:
        """Show open directory dialog."""
        initial_dir = str(self.project_path) if self.project_path else str(Path.home())
        chosen_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            initial_dir,
            QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks,
        )
        if chosen_dir:
            self.set_project_path(chosen_dir)

    def _show_context_menu(self, position) -> None:
        """Display right-click context menu on tree view items."""
        menu = QMenu(self)

        # Context menu items defined for Phase 1 / Phase 3
        action_refresh = QAction("Refresh", self)
        action_refresh.triggered.connect(self.refresh)
        menu.addAction(action_refresh)

        menu.addSeparator()

        action_open_folder = QAction("Open Folder...", self)
        action_open_folder.triggered.connect(self._on_open_folder_clicked)
        menu.addAction(action_open_folder)

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

