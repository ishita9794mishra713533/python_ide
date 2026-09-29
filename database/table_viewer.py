"""Table Data and Schema viewer component with complete CRUD capabilities."""
from typing import Optional, Dict, Any, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QPlainTextEdit,
    QMessageBox,
    QDialog,
)

from utils.logger import get_logger
from database.sqlite_manager import SQLiteManager
from database.crud_manager import CRUDManager
from database.models import TableSchema
from dialogs.record_dialog import RecordDialog

logger = get_logger("table_viewer")


class TableViewerWidget(QWidget):
    """Complete Table Viewer & Editor with Data grid, CRUD operations, Search, and Schema."""

    table_data_changed = Signal(str)

    def __init__(
        self,
        table_name: str,
        sqlite_manager: SQLiteManager,
        crud_manager: CRUDManager,
        parent=None,
    ):
        super().__init__(parent)
        self.table_name = table_name
        self.sqlite_manager = sqlite_manager
        self.crud_manager = crud_manager
        self.schema: Optional[TableSchema] = None

        self._setup_ui()
        self.refresh_all()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        self.tabs = QTabWidget(self)

        # 1. Data Tab
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        data_layout.setContentsMargins(4, 4, 4, 4)
        data_layout.setSpacing(6)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.table_info_label = QLabel(f"Table: <b>{self.table_name}</b>")
        self.table_info_label.setStyleSheet("font-size: 13px; color: #ffffff;")
        toolbar.addWidget(self.table_info_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search / filter table...")
        self.search_input.setMaximumWidth(280)
        self.search_input.returnPressed.connect(self.load_data)
        toolbar.addWidget(self.search_input)

        btn_search = QPushButton("Filter")
        btn_search.clicked.connect(self.load_data)
        toolbar.addWidget(btn_search)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self._clear_filter)
        toolbar.addWidget(btn_clear)

        toolbar.addStretch()

        btn_insert = QPushButton("+ Insert Row")
        btn_insert.clicked.connect(self.insert_row)
        toolbar.addWidget(btn_insert)

        btn_edit = QPushButton("Edit Row")
        btn_edit.clicked.connect(self.edit_selected_row)
        toolbar.addWidget(btn_edit)

        btn_delete = QPushButton("Delete Row")
        btn_delete.setStyleSheet("background-color: #8b0000; color: #ffffff;")
        btn_delete.clicked.connect(self.delete_selected_row)
        toolbar.addWidget(btn_delete)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh_all)
        toolbar.addWidget(btn_refresh)

        data_layout.addLayout(toolbar)

        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.data_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.doubleClicked.connect(lambda idx: self.edit_selected_row())
        data_layout.addWidget(self.data_table)

        self.status_label = QLabel("0 rows")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        data_layout.addWidget(self.status_label)

        self.tabs.addTab(data_tab, "Data View")

        # 2. Schema Tab
        schema_tab = QWidget()
        schema_layout = QVBoxLayout(schema_tab)
        schema_layout.setContentsMargins(4, 4, 4, 4)
        schema_layout.setSpacing(6)

        schema_title = QLabel(f"Structure & Constraints for '{self.table_name}'")
        schema_title.setStyleSheet("font-weight: 600;")
        schema_layout.addWidget(schema_title)

        self.schema_table = QTableWidget(0, 6)
        self.schema_table.setHorizontalHeaderLabels([
            "CID", "Column Name", "Data Type", "Primary Key", "Not Null", "Default Value"
        ])
        self.schema_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        schema_layout.addWidget(self.schema_table)

        ddl_label = QLabel("CREATE TABLE Statement:")
        ddl_label.setStyleSheet("font-weight: 600; margin-top: 6px;")
        schema_layout.addWidget(ddl_label)

        self.ddl_view = QPlainTextEdit()
        self.ddl_view.setReadOnly(True)
        self.ddl_view.setStyleSheet("font-family: 'Consolas'; background-color: #1e1e1e; color: #ce9178;")
        self.ddl_view.setMaximumHeight(160)
        schema_layout.addWidget(self.ddl_view)

        self.tabs.addTab(schema_tab, "Structure")

        main_layout.addWidget(self.tabs)

    def refresh_all(self) -> None:
        self.schema = self.sqlite_manager.get_table_schema(self.table_name)
        if not self.schema:
            return

        self.load_schema()
        self.load_data()

    def load_schema(self) -> None:
        if not self.schema:
            return

        self.schema_table.setRowCount(0)
        for row_idx, col in enumerate(self.schema.columns):
            self.schema_table.insertRow(row_idx)
            self.schema_table.setItem(row_idx, 0, QTableWidgetItem(str(col.cid)))
            self.schema_table.setItem(row_idx, 1, QTableWidgetItem(col.name))
            self.schema_table.setItem(row_idx, 2, QTableWidgetItem(col.data_type))
            self.schema_table.setItem(row_idx, 3, QTableWidgetItem("YES 🔑" if col.is_primary_key else "No"))
            self.schema_table.setItem(row_idx, 4, QTableWidgetItem("YES" if col.not_null else "No"))
            self.schema_table.setItem(row_idx, 5, QTableWidgetItem(str(col.default_value) if col.default_value is not None else "NULL"))

        self.ddl_view.setPlainText(self.schema.sql or "-- No DDL available")

    def load_data(self) -> None:
        search_kw = self.search_input.text().strip()
        result = self.crud_manager.select_data(self.table_name, search_filter=search_kw)

        if not result.success:
            QMessageBox.critical(self, "Query Error", result.error_message or "Failed to load data.")
            return

        self.data_table.clear()
        self.data_table.setColumnCount(len(result.columns))
        self.data_table.setHorizontalHeaderLabels(result.columns)
        self.data_table.setRowCount(len(result.rows))

        for row_idx, row_data in enumerate(result.rows):
            for col_idx, cell_value in enumerate(row_data):
                display_val = "NULL" if cell_value is None else str(cell_value)
                item = QTableWidgetItem(display_val)
                if cell_value is None:
                    item.setForeground(Qt.GlobalColor.darkGray)
                self.data_table.setItem(row_idx, col_idx, item)

        total_count = self.sqlite_manager.get_row_count(self.table_name)
        filter_str = f" (filtered from {total_count})" if search_kw else ""
        self.status_label.setText(f"Showing {len(result.rows)} of {total_count} rows{filter_str} | Execution: {result.execution_time_ms:.2f} ms")

    def _clear_filter(self) -> None:
        self.search_input.clear()
        self.load_data()

    def _get_row_data(self, row_idx: int) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for col_idx in range(self.data_table.columnCount()):
            col_name = self.data_table.horizontalHeaderItem(col_idx).text()
            item = self.data_table.item(row_idx, col_idx)
            val = item.text() if item else ""
            data[col_name] = None if val == "NULL" else val
        return data

    def _get_key_conditions(self, row_idx: int) -> Dict[str, Any]:
        row_dict = self._get_row_data(row_idx)
        if not self.schema:
            return row_dict

        pks = self.schema.get_primary_keys()
        if pks:
            return {k: row_dict[k] for k in pks if k in row_dict}
        return row_dict

    def insert_row(self) -> None:
        if not self.schema:
            return

        dialog = RecordDialog(self.schema, parent=self)
        if dialog.exec():
            new_data = dialog.get_data()
            res = self.crud_manager.insert_record(self.table_name, new_data)
            if res.success:
                self.load_data()
                self.table_data_changed.emit(self.table_name)
            else:
                QMessageBox.critical(self, "Insert Error", res.error_message or "Failed to insert record.")

    def edit_selected_row(self) -> None:
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a row to edit.")
            return

        row_idx = selected_rows[0].row()
        current_data = self._get_row_data(row_idx)
        key_conditions = self._get_key_conditions(row_idx)

        if not self.schema:
            return

        dialog = RecordDialog(self.schema, existing_data=current_data, parent=self)
        if dialog.exec():
            updated_data = dialog.get_data()
            res = self.crud_manager.update_record(self.table_name, updated_data, key_conditions)
            if res.success:
                self.load_data()
                self.table_data_changed.emit(self.table_name)
            else:
                QMessageBox.critical(self, "Update Error", res.error_message or "Failed to update record.")

    def delete_selected_row(self) -> None:
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a row to delete.")
            return

        row_idx = selected_rows[0].row()
        key_conditions = self._get_key_conditions(row_idx)

        reply = QMessageBox.warning(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this record?\n\nKey: {key_conditions}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        res = self.crud_manager.delete_record(self.table_name, key_conditions)
        if res.success:
            self.load_data()
            self.table_data_changed.emit(self.table_name)
        else:
            QMessageBox.critical(self, "Delete Error", res.error_message or "Failed to delete record.")


class TableViewerDialog(QDialog):
    """Dialog wrapper around TableViewerWidget."""

    def __init__(self, sqlite_manager: SQLiteManager, table_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Table Viewer - {table_name}")
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.viewer = TableViewerWidget(
            table_name=table_name,
            sqlite_manager=sqlite_manager,
            crud_manager=CRUDManager(sqlite_manager),
            parent=self,
        )
        layout.addWidget(self.viewer)
