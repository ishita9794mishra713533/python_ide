"""Database Explorer dock panel showing SQLite databases, tables, and views hierarchy."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QToolButton,
    QFileDialog,
    QMenu,
    QMessageBox,
)
from PySide6.QtGui import QAction, QFont

from utils.logger import get_logger
from database.sqlite_manager import SQLiteManager
from database.crud_manager import CRUDManager
from dialogs.create_table_dialog import CreateTableDialog

logger = get_logger("database_explorer")


class DatabaseExplorerWidget(QWidget):
    """Database panel displaying SQLite connection, tables, and views with CRUD triggers."""

    table_open_requested = Signal(str)
    table_selected = Signal(str)
    schema_view_requested = Signal(str)
    sql_console_requested = Signal()
    database_connected = Signal(Path)
    database_closed = Signal()

    def __init__(
        self,
        sqlite_manager: SQLiteManager,
        crud_manager: Optional[CRUDManager] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.sqlite_manager = sqlite_manager
        self.crud_manager = crud_manager or CRUDManager(sqlite_manager)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setStyleSheet(
            "background-color: #252526; border-bottom: 1px solid #333333; padding: 4px;"
        )
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 4, 4)
        header_layout.setSpacing(4)

        self.db_title_label = QLabel("NO DATABASE CONNECTED")
        self.db_title_label.setStyleSheet("font-weight: 600; font-size: 11px; color: #bbbbbb;")
        header_layout.addWidget(self.db_title_label, stretch=1)

        self.btn_new_db = QToolButton()
        self.btn_new_db.setText("➕DB")
        self.btn_new_db.setToolTip("Create SQLite Database")
        self.btn_new_db.clicked.connect(self.create_new_database)
        header_layout.addWidget(self.btn_new_db)

        self.btn_open_db = QToolButton()
        self.btn_open_db.setText("📂")
        self.btn_open_db.setToolTip("Open Existing Database (.db, .sqlite)")
        self.btn_open_db.clicked.connect(self.open_database_dialog)
        header_layout.addWidget(self.btn_open_db)

        self.btn_new_table = QToolButton()
        self.btn_new_table.setText("➕Tbl")
        self.btn_new_table.setToolTip("Create Table in Active Database")
        self.btn_new_table.clicked.connect(self.create_new_table)
        header_layout.addWidget(self.btn_new_table)

        self.btn_sql = QToolButton()
        self.btn_sql.setText("⚡SQL")
        self.btn_sql.setToolTip("Open SQL Query Console")
        self.btn_sql.clicked.connect(self.sql_console_requested.emit)
        header_layout.addWidget(self.btn_sql)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setText("🔄")
        self.btn_refresh.setToolTip("Refresh Database")
        self.btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(self.btn_refresh)

        layout.addWidget(header_widget)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.tree)

    def connect_database(self, db_path: Path | str) -> bool:
        success, msg = self.sqlite_manager.connect(db_path)
        if success and self.sqlite_manager.db_path:
            self.db_title_label.setText(self.sqlite_manager.db_path.name.upper())
            self.refresh()
            self.database_connected.emit(self.sqlite_manager.db_path)
            return True
        else:
            QMessageBox.critical(self, "Connection Error", msg)
            return False

    def create_new_database(self) -> None:
        chosen_file, _ = QFileDialog.getSaveFileName(
            self,
            "Create SQLite Database",
            "app.db",
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*.*)",
        )
        if chosen_file:
            success, msg = self.sqlite_manager.create_database(chosen_file)
            if success and self.sqlite_manager.db_path:
                self.db_title_label.setText(self.sqlite_manager.db_path.name.upper())
                self.refresh()
                self.database_connected.emit(self.sqlite_manager.db_path)
            else:
                QMessageBox.critical(self, "Creation Error", msg)

    def open_database_dialog(self) -> None:
        chosen_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open SQLite Database",
            "",
            "SQLite Databases (*.db *.sqlite *.sqlite3);;All Files (*.*)",
        )
        if chosen_file:
            self.connect_database(chosen_file)

    def disconnect_database(self) -> None:
        self.sqlite_manager.disconnect()
        self.db_title_label.setText("NO DATABASE CONNECTED")
        self.tree.clear()
        self.database_closed.emit()

    def refresh(self) -> None:
        self.tree.clear()
        if not self.sqlite_manager.is_connected() or not self.sqlite_manager.db_path:
            return

        root_node = QTreeWidgetItem(["SQLite"])
        font = QFont()
        font.setBold(True)
        root_node.setFont(0, font)

        db_node = QTreeWidgetItem([f"📁 {self.sqlite_manager.db_path.name}"])
        root_node.addChild(db_node)

        tables = self.sqlite_manager.get_tables()
        tables_node = QTreeWidgetItem([f"Tables ({len(tables)})"])
        for tbl in tables:
            count = self.sqlite_manager.get_row_count(tbl)
            tbl_item = QTreeWidgetItem([f"📊 {tbl} ({count})"])
            tbl_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "table", "name": tbl})
            tables_node.addChild(tbl_item)
        db_node.addChild(tables_node)

        views = self.sqlite_manager.get_views()
        views_node = QTreeWidgetItem([f"Views ({len(views)})"])
        for vw in views:
            vw_item = QTreeWidgetItem([f"👁 {vw}"])
            vw_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "view", "name": vw})
            views_node.addChild(vw_item)
        db_node.addChild(views_node)

        self.tree.addTopLevelItem(root_node)
        self.tree.expandAll()

    def create_new_table(self) -> None:
        if not self.sqlite_manager.is_connected():
            QMessageBox.information(self, "No Database", "Please connect to a database first.")
            return

        dialog = CreateTableDialog(self)
        if dialog.exec():
            tbl_name, cols = dialog.get_result()
            res = self.crud_manager.create_table(tbl_name, cols)
            if res.success:
                self.refresh()
                self.table_open_requested.emit(tbl_name)
            else:
                QMessageBox.critical(self, "Create Table Error", res.error_message or "Failed to create table.")

    def delete_table(self, table_name: str) -> None:
        reply = QMessageBox.warning(
            self,
            "Confirm Drop Table",
            f"Are you sure you want to permanently drop table '{table_name}' and all its data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            res = self.crud_manager.drop_table(table_name)
            if res.success:
                self.refresh()
            else:
                QMessageBox.critical(self, "Error", res.error_message or "Failed to drop table.")

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get("type") in ("table", "view"):
            self.table_open_requested.emit(data["name"])
            self.table_selected.emit(data["name"])

    def _show_context_menu(self, position) -> None:
        item = self.tree.itemAt(position)
        menu = QMenu(self)

        if item:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("type") == "table":
                tbl_name = data["name"]

                action_view_data = QAction(f"View Data ({tbl_name})", self)
                action_view_data.triggered.connect(lambda: self.table_open_requested.emit(tbl_name))
                menu.addAction(action_view_data)

                action_view_schema = QAction("View Structure", self)
                action_view_schema.triggered.connect(lambda: self.schema_view_requested.emit(tbl_name))
                menu.addAction(action_view_schema)

                menu.addSeparator()

                action_drop = QAction(f"Drop Table '{tbl_name}'", self)
                action_drop.triggered.connect(lambda: self.delete_table(tbl_name))
                menu.addAction(action_drop)
                menu.addSeparator()

        action_new_table = QAction("Create New Table...", self)
        action_new_table.setEnabled(self.sqlite_manager.is_connected())
        action_new_table.triggered.connect(self.create_new_table)
        menu.addAction(action_new_table)

        action_sql = QAction("Open SQL Console", self)
        action_sql.setEnabled(self.sqlite_manager.is_connected())
        action_sql.triggered.connect(self.sql_console_requested.emit)
        menu.addAction(action_sql)

        action_refresh = QAction("Refresh", self)
        action_refresh.triggered.connect(self.refresh)
        menu.addAction(action_refresh)

        menu.exec(self.tree.viewport().mapToGlobal(position))


# Alias for backward compatibility
DatabaseExplorer = DatabaseExplorerWidget
