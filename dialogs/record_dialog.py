"""Modal dialog for inserting or editing a database record."""
from typing import Dict, Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QScrollArea,
    QWidget,
    QMessageBox,
)

from database.models import TableSchema


class RecordDialog(QDialog):
    """Dynamically generates input fields based on table schema for inserting or editing rows."""

    def __init__(
        self,
        schema: TableSchema,
        existing_data: Optional[Dict[str, Any]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.schema = schema
        self.existing_data = existing_data or {}
        self.is_edit_mode = bool(existing_data)
        self.fields: Dict[str, QLineEdit] = {}

        self.setWindowTitle(f"{'Edit' if self.is_edit_mode else 'Insert'} Row - {schema.name}")
        self.resize(450, min(500, 150 + len(schema.columns) * 45))
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Form scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)

        for col in self.schema.columns:
            label_text = f"{col.name}"
            if col.is_primary_key:
                label_text += " 🔑"
            if col.not_null:
                label_text += " *"
            label_text += f" ({col.data_type}):"

            lbl = QLabel(label_text)
            if col.is_primary_key:
                lbl.setStyleSheet("color: #007acc; font-weight: 600;")

            line_edit = QLineEdit()
            if self.is_edit_mode and col.name in self.existing_data:
                val = self.existing_data[col.name]
                line_edit.setText("" if val is None else str(val))
            elif col.default_value is not None:
                line_edit.setText(str(col.default_value))

            if self.is_edit_mode and col.is_primary_key:
                line_edit.setReadOnly(True)
                line_edit.setStyleSheet("background-color: #2b2b2b; color: #888888;")

            self.fields[col.name] = line_edit
            form_layout.addRow(lbl, line_edit)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

        # Dialog Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Save Changes" if self.is_edit_mode else "Insert Row")
        btn_save.setDefault(True)
        btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

    def _on_save(self) -> None:
        data: Dict[str, Any] = {}
        for col in self.schema.columns:
            raw_val = self.fields[col.name].text().strip()

            if not raw_val:
                if col.not_null and not (col.is_primary_key and not self.is_edit_mode):
                    QMessageBox.critical(self, "Validation Error", f"Column '{col.name}' cannot be empty (NOT NULL).")
                    return
                if col.is_primary_key and not self.is_edit_mode:
                    continue
                data[col.name] = None
                continue

            dtype = col.data_type.upper()
            try:
                if "INT" in dtype:
                    data[col.name] = int(raw_val)
                elif "REAL" in dtype or "FLOAT" in dtype or "DOUB" in dtype:
                    data[col.name] = float(raw_val)
                else:
                    data[col.name] = raw_val
            except ValueError:
                QMessageBox.critical(
                    self,
                    "Type Error",
                    f"Value '{raw_val}' is invalid for column '{col.name}' ({col.data_type}).",
                )
                return

        self.result_data = data
        self.accept()

    def get_data(self) -> Dict[str, Any]:
        return getattr(self, "result_data", {})
