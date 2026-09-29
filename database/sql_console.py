"""SQL Query Console component for executing arbitrary SQL queries with results table."""
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QSplitter,
    QMessageBox,
)
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from utils.logger import get_logger
from database.sqlite_manager import SQLiteManager
from database.models import QueryResult

logger = get_logger("sql_console")


class SQLConsoleWidget(QWidget):
    """SQL Console with multi-line query editor, execution trigger, and results table."""

    query_executed = Signal(QueryResult)

    def __init__(self, sqlite_manager: SQLiteManager, parent=None):
        super().__init__(parent)
        self.sqlite_manager = sqlite_manager
        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        title_label = QLabel("SQL Query Console")
        title_label.setStyleSheet("font-weight: 700; color: #ffffff;")
        toolbar.addWidget(title_label)

        toolbar.addStretch()

        self.btn_run = QPushButton("▶ Run Query (Ctrl+Enter)")
        self.btn_run.setStyleSheet("background-color: #0e639c; color: #ffffff; font-weight: bold;")
        self.btn_run.clicked.connect(self.run_query)
        toolbar.addWidget(self.btn_run)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_console)
        toolbar.addWidget(self.btn_clear)

        main_layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Orientation.Vertical)

        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(4)

        self.sql_editor = QPlainTextEdit()
        self.sql_editor.setPlaceholderText("-- Write SQLite query here, e.g.:\nSELECT * FROM sqlite_master;")
        self.sql_editor.setStyleSheet(
            "QPlainTextEdit { background-color: #1e1e1e; color: #d4d4d4; "
            "font-family: 'Consolas'; font-size: 13px; border: 1px solid #3c3c3c; }"
        )
        editor_layout.addWidget(self.sql_editor)
        splitter.addWidget(editor_container)

        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(4)

        self.status_bar_label = QLabel("Ready")
        self.status_bar_label.setStyleSheet("color: #888888; font-size: 11px;")
        results_layout.addWidget(self.status_bar_label)

        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)

        splitter.addWidget(results_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.run_query)

    def set_query_text(self, sql: str) -> None:
        self.sql_editor.setPlainText(sql)

    def clear_console(self) -> None:
        self.sql_editor.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.status_bar_label.setText("Cleared.")
        self.status_bar_label.setStyleSheet("color: #888888;")

    def run_query(self) -> None:
        if not self.sqlite_manager.is_connected():
            self.status_bar_label.setText("Error: No active database connected.")
            self.status_bar_label.setStyleSheet("color: #f14c4c; font-weight: bold;")
            return

        sql = self.sql_editor.toPlainText().strip()
        if not sql:
            self.status_bar_label.setText("Query is empty.")
            return

        result = self.sqlite_manager.executor.execute_query(sql)

        if not result.success:
            self.status_bar_label.setText(f"SQL Error: {result.error_message}")
            self.status_bar_label.setStyleSheet("color: #f14c4c; font-weight: bold;")
            self.results_table.clear()
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return

        self.results_table.clear()
        self.results_table.setColumnCount(len(result.columns))
        self.results_table.setHorizontalHeaderLabels(result.columns)
        self.results_table.setRowCount(len(result.rows))

        for row_idx, row_data in enumerate(result.rows):
            for col_idx, cell_value in enumerate(row_data):
                display_val = "NULL" if cell_value is None else str(cell_value)
                item = QTableWidgetItem(display_val)
                if cell_value is None:
                    item.setForeground(Qt.GlobalColor.darkGray)
                self.results_table.setItem(row_idx, col_idx, item)

        if result.columns:
            msg = f"Returned {len(result.rows)} rows in {result.execution_time_ms:.2f} ms"
        else:
            msg = f"Query executed successfully ({result.rows_affected} rows affected) in {result.execution_time_ms:.2f} ms"

        self.status_bar_label.setText(msg)
        self.status_bar_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        self.query_executed.emit(result)

    def update_connection_status(self) -> None:
        """Update status label based on database connection state."""
        if self.sqlite_manager.is_connected():
            db_name = self.sqlite_manager.db_path.name if self.sqlite_manager.db_path else "Connected"
            self.status_bar_label.setText(f"Connected to {db_name}")
            self.status_bar_label.setStyleSheet("color: #4ec9b0;")
        else:
            self.status_bar_label.setText("No database connected.")
            self.status_bar_label.setStyleSheet("color: #888888;")


# Alias for backward compatibility
SQLConsole = SQLConsoleWidget
