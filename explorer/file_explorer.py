"""File explorer dock widget implementing Qt Model/View architecture with CRUD operations."""
import os
import subprocess
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
from PySide6.QtGui import QAction, QKeySequence

from utils.logger import get_logger
from explorer.file_manager import FileManager
from dialogs.new_file_dialog import NewFileDialog
from dialogs.new_folder_dialog import NewFolderDialog
from dialogs.rename_dialog import RenameDialog

logger = get_logger("file_explorer")


class FileExplorerWidget(QWidget):
    """File Explorer panel showing project tree using QFileSystemModel with CRUD operations."""

    # Signals
    file_double_clicked = Signal(Path)
    file_opened = Signal(str)
    file_selected = Signal(Path)
    project_opened = Signal(Path)
    file_created = Signal(Path)
    folder_created = Signal(Path)
    item_renamed = Signal(Path, Path)   # (old_path, new_path)
    item_deleted = Signal(Path)

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
        self.btn_new_file = QToolButton()
        self.btn_new_file.setText("📄")
        self.btn_new_file.setToolTip("New File")
        self.btn_new_file.clicked.connect(self.create_new_file)
        header_layout.addWidget(self.btn_new_file)

        self.btn_new_folder = QToolButton()
        self.btn_new_folder.setText("📁+")
        self.btn_new_folder.setToolTip("New Folder")
        self.btn_new_folder.clicked.connect(self.create_new_folder)
        header_layout.addWidget(self.btn_new_folder)

        self.btn_open = QToolButton()
        self.btn_open.setText("📂")
        self.btn_open.setToolTip("Open Project Folder")
        self.btn_open.clicked.connect(self._on_open_folder_clicked)
        header_layout.addWidget(self.btn_open)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setText("🔄")
        self.btn_refresh.setToolTip("Refresh Explorer (F5)")
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

        # Hide Size, Type, Date Modified columns
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

    def set_root_path(self, path: Path | str) -> bool:
        """Alias for set_project_path."""
        return self.set_project_path(path)

    def get_root_path(self) -> Optional[str]:
        """Return current root path string or None."""
        return str(self.project_path) if self.project_path else None

    def refresh(self) -> None:
        """Refresh the filesystem model."""
        if self.project_path:
            logger.debug("Refreshing filesystem model for: %s", self.project_path)
            self.fs_model.setRootPath(str(self.project_path))
            root_idx = self.fs_model.index(str(self.project_path))
            self.tree_view.setRootIndex(root_idx)

    def collapse_all(self) -> None:
        """Collapse all expanded directories."""
        self.tree_view.collapseAll()

    def get_selected_path(self) -> Optional[Path]:
        """Get the filesystem Path of the currently selected item or None."""
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return None
        file_path_str = self.fs_model.filePath(indexes[0])
        return Path(file_path_str).resolve() if file_path_str else None

    def get_target_directory_for_creation(self) -> Optional[Path]:
        """Determine parent directory for creating a new file or folder."""
        selected = self.get_selected_path()
        if selected:
            return selected if selected.is_dir() else selected.parent
        return self.project_path

    # CRUD Operations
    def create_new_file(self) -> Optional[Path]:
        """Show dialog and create a new file."""
        target_dir = self.get_target_directory_for_creation()
        if not target_dir:
            QMessageBox.information(self, "No Project", "Please open a project folder first.")
            return None

        dialog = NewFileDialog(target_dir, self)
        if dialog.exec():
            filename = dialog.get_filename()
            success, msg, created_path = FileManager.create_file(target_dir, filename)
            if success and created_path:
                self.refresh()
                self.file_created.emit(created_path)
                self.file_double_clicked.emit(created_path)
                return created_path
            else:
                QMessageBox.critical(self, "Create File Error", msg)
        return None

    def create_new_folder(self) -> Optional[Path]:
        """Show dialog and create a new folder."""
        target_dir = self.get_target_directory_for_creation()
        if not target_dir:
            QMessageBox.information(self, "No Project", "Please open a project folder first.")
            return None

        dialog = NewFolderDialog(target_dir, self)
        if dialog.exec():
            foldername = dialog.get_foldername()
            success, msg, created_path = FileManager.create_folder(target_dir, foldername)
            if success and created_path:
                self.refresh()
                self.folder_created.emit(created_path)
                return created_path
            else:
                QMessageBox.critical(self, "Create Folder Error", msg)
        return None

    def rename_selected(self) -> Optional[Path]:
        """Rename the currently selected file or directory."""
        selected = self.get_selected_path()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a file or folder to rename.")
            return None

        if self.project_path and selected == self.project_path:
            QMessageBox.warning(self, "Rename", "Cannot rename the root project folder.")
            return None

        dialog = RenameDialog(selected, self)
        if dialog.exec():
            new_name = dialog.get_new_name()
            success, msg, new_path = FileManager.rename_item(selected, new_name)
            if success and new_path:
                self.refresh()
                self.item_renamed.emit(selected, new_path)
                return new_path
            else:
                QMessageBox.critical(self, "Rename Error", msg)
        return None

    def delete_selected(self) -> bool:
        """Delete the currently selected file or directory with confirmation."""
        selected = self.get_selected_path()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select an item to delete.")
            return False

        if self.project_path and selected == self.project_path:
            QMessageBox.warning(self, "Delete", "Cannot delete the root project folder.")
            return False

        # Extra safety check: prevent deleting SmartIDE code directory
        if selected.name.lower() == "smartide" or str(selected).lower().endswith("smartide"):
            QMessageBox.critical(self, "Protected Folder", "SmartIDE application source folder cannot be deleted.")
            return False

        item_type = "folder and all its contents" if selected.is_dir() else "file"
        reply = QMessageBox.warning(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete this {item_type}?\n\n'{selected.name}'\n({selected})",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return False

        success, msg = FileManager.delete_item(selected)
        if success:
            self.refresh()
            self.item_deleted.emit(selected)
            return True
        else:
            QMessageBox.critical(self, "Delete Error", msg)
            return False

    def reveal_in_explorer(self) -> None:
        """Open system file manager at current selected item or project directory."""
        target = self.get_selected_path() or self.project_path
        if not target or not target.exists():
            return

        try:
            if os.name == "nt":
                if target.is_file():
                    subprocess.run(["explorer", f"/select,{target}"], check=False)
                else:
                    subprocess.run(["explorer", str(target)], check=False)
            elif os.name == "posix":
                subprocess.run(["xdg-open", str(target.parent if target.is_file() else target)], check=False)
        except Exception as e:
            logger.warning("Could not open system explorer: %s", e)

    def _show_context_menu(self, position) -> None:
        """Display right-click context menu on tree view items."""
        index = self.tree_view.indexAt(position)
        selected_path = None
        if index.isValid():
            p_str = self.fs_model.filePath(index)
            if p_str:
                selected_path = Path(p_str).resolve()

        menu = QMenu(self)

        # 1. New File / Folder
        action_new_file = QAction("New File...", self)
        action_new_file.triggered.connect(self.create_new_file)
        menu.addAction(action_new_file)

        action_new_folder = QAction("New Folder...", self)
        action_new_folder.triggered.connect(self.create_new_folder)
        menu.addAction(action_new_folder)

        menu.addSeparator()

        # 2. Rename & Delete
        is_item_selected = selected_path is not None and selected_path != self.project_path

        action_rename = QAction("Rename...", self)
        action_rename.setShortcut(QKeySequence("F2"))
        action_rename.setEnabled(is_item_selected)
        action_rename.triggered.connect(self.rename_selected)
        menu.addAction(action_rename)

        action_delete = QAction("Delete", self)
        action_delete.setShortcut(QKeySequence.StandardKey.Delete)
        action_delete.setEnabled(is_item_selected)
        action_delete.triggered.connect(self.delete_selected)
        menu.addAction(action_delete)

        menu.addSeparator()

        # 3. Refresh & Reveal
        action_refresh = QAction("Refresh", self)
        action_refresh.triggered.connect(self.refresh)
        menu.addAction(action_refresh)

        action_reveal = QAction("Reveal in System Explorer", self)
        action_reveal.triggered.connect(self.reveal_in_explorer)
        menu.addAction(action_reveal)

        menu.addSeparator()

        action_open_folder = QAction("Open Project Folder...", self)
        action_open_folder.triggered.connect(self._on_open_folder_clicked)
        menu.addAction(action_open_folder)

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def keyPressEvent(self, event) -> None:
        """Handle keyboard shortcuts in tree view (F2 = rename, Del = delete, F5 = refresh)."""
        if event.key() == Qt.Key.Key_F2:
            self.rename_selected()
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
            event.accept()
        elif event.key() == Qt.Key.Key_F5:
            self.refresh()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _on_tree_double_clicked(self, index: QModelIndex) -> None:
        """Handle double click on tree item."""
        file_path_str = self.fs_model.filePath(index)
        if not file_path_str:
            return

        p = Path(file_path_str)
        if p.is_file():
            logger.info("File double clicked: %s", p)
            self.file_double_clicked.emit(p)
            self.file_opened.emit(str(p))

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
