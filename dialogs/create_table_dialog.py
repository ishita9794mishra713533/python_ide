"""Modal dialog for creating a new SQLite table."""
from typing import List, Dict, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QCheckBox,
    QHeaderView,
    QMessageBox,
    QWidget,
)

DATA_TYPES = ["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"]


class CreateTableDialog(QDialog):
    """Dialog allowing user to define table name, columns, types, and constraints."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create SQLite Table")
        self.resize(550, 400)
        self.setModal(True)

        self.table_name: str = ""
        self.columns: List[Dict[str, Any]] = []

        self._setup_ui()
        self._add_column_row("id", "INTEGER", is_pk=True, not_null=True)
        self._add_column_row("name", "TEXT", is_pk=False, not_null=False)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 1. Table Name row
        name_layout = QHBoxLayout()
        name_label = QLabel("Table Name:")
        name_label.setStyleSheet("font-weight: 600;")
        self.table_name_input = QLineEdit()
        self.table_name_input.setPlaceholderText("e.g. students, products, orders")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.table_name_input)
        layout.addLayout(name_layout)

        # 2. Columns Table
        col_header_layout = QHBoxLayout()
        col_title = QLabel("Columns Definition:")
        col_title.setStyleSheet("font-weight: 600;")
        col_header_layout.addWidget(col_title)
        col_header_layout.addStretch()

        btn_add_col = QPushButton("+ Add Column")
        btn_add_col.clicked.connect(lambda: self._add_column_row())
        col_header_layout.addWidget(btn_add_col)

        btn_remove_col = QPushButton("- Remove Selected")
        btn_remove_col.clicked.connect(self._remove_selected_column)
        col_header_layout.addWidget(btn_remove_col)

        layout.addLayout(col_header_layout)

        self.table_widget = QTableWidget(0, 4)
        self.table_widget.setHorizontalHeaderLabels(["Column Name", "Data Type", "Primary Key", "Not Null"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table_widget)

        # 3. Dialog Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_create = QPushButton("Create Table")
        btn_create.setDefault(True)
        btn_create.clicked.connect(self._on_create)
        btn_layout.addWidget(btn_create)

        layout.addLayout(btn_layout)

    def _add_column_row(
        self,
        name: str = "",
        dtype: str = "TEXT",
        is_pk: bool = False,
        not_null: bool = False,
    ) -> None:
        """Add a new column definition row."""
        row_idx = self.table_widget.rowCount()
        self.table_widget.insertRow(row_idx)

        # Column Name
        name_item = QLineEdit(name)
        name_item.setPlaceholderText(f"col_{row_idx + 1}")
        self.table_widget.setCellWidget(row_idx, 0, name_item)

        # Data Type ComboBox
        type_combo = QComboBox()
        type_combo.addItems(DATA_TYPES)
        if dtype.upper() in DATA_TYPES:
            type_combo.setCurrentText(dtype.upper())
        self.table_widget.setCellWidget(row_idx, 1, type_combo)

        # Primary Key CheckBox
        pk_check = QCheckBox()
        pk_check.setChecked(is_pk)
        pk_widget = QWidget()
        pk_layout = QHBoxLayout(pk_widget)
        pk_layout.addWidget(pk_check)
        pk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pk_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget.setCellWidget(row_idx, 2, pk_widget)

        # Not Null CheckBox
        nn_check = QCheckBox()
        nn_check.setChecked(not_null)
        nn_widget = QWidget()
        nn_layout = QHBoxLayout(nn_widget)
        nn_layout.addWidget(nn_check)
        nn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nn_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget.setCellWidget(row_idx, 3, nn_widget)

    def _remove_selected_column(self) -> None:
        """Remove the selected row in the column table."""
        current_row = self.table_widget.currentRow()
        if current_row != -1:
            self.table_widget.removeRow(current_row)

    def _on_create(self) -> None:
        """Validate input and prepare column definitions."""
        table_name = self.table_name_input.text().strip()
        if not table_name:
            QMessageBox.critical(self, "Validation Error", "Please provide a valid table name.")
            return

        row_count = self.table_widget.rowCount()
        if row_count == 0:
            QMessageBox.critical(self, "Validation Error", "Please add at least one column.")
            return

        cols: List[Dict[str, Any]] = []
        for row in range(row_count):
            name_widget = self.table_widget.cellWidget(row, 0)
            col_name = name_widget.text().strip() if isinstance(name_widget, QLineEdit) else ""
            if not col_name:
                QMessageBox.critical(self, "Validation Error", f"Column #{row + 1} has an empty name.")
                return

            type_widget = self.table_widget.cellWidget(row, 1)
            col_type = type_widget.currentText() if isinstance(type_widget, QComboBox) else "TEXT"

            pk_container = self.table_widget.cellWidget(row, 2)
            pk_box = pk_container.findChild(QCheckBox) if pk_container else None
            is_pk = pk_box.isChecked() if pk_box else False

            nn_container = self.table_widget.cellWidget(row, 3)
            nn_box = nn_container.findChild(QCheckBox) if nn_container else None
            is_nn = nn_box.isChecked() if nn_box else False

            cols.append({
                "name": col_name,
                "type": col_type,
                "primary_key": is_pk,
                "not_null": is_nn,
            })

        self.table_name = table_name
        self.columns = cols
        self.accept()

    def get_result(self) -> tuple[str, List[Dict[str, Any]]]:
        """Return table name and list of column definitions."""
        return self.table_name, self.columns
