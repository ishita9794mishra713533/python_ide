"""Modal dialog for creating a new file."""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)



class NewFileDialog(QDialog):
    """Dialog to prompt user for new file name."""

    def __init__(self, parent_dir: Path, parent=None):
        super().__init__(parent)
        self.parent_dir = parent_dir
        self.filename: str = ""

        self.setWindowTitle("New File")
        self.setFixedSize(380, 160)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Parent directory hint
        parent_label = QLabel(f"Create in: <b>{self.parent_dir.name}/</b>")
        parent_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(parent_label)

        # Name label
        label = QLabel("File name:")
        label.setStyleSheet("font-weight: 500;")
        layout.addWidget(label)

        # Input
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("e.g. app.py, utils.py")
        self.name_input.textChanged.connect(self._validate_input)
        layout.addWidget(self.name_input)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f14c4c; font-size: 11px;")
        layout.addWidget(self.error_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_create = QPushButton("Create File", self)
        self.btn_create.setEnabled(False)
        self.btn_create.setDefault(True)
        self.btn_create.clicked.connect(self._on_create)
        btn_layout.addWidget(self.btn_create)

        layout.addLayout(btn_layout)

    def _validate_input(self, text: str) -> None:
        valid, msg = FileManager.validate_name(text)
        if not text.strip():
            self.error_label.setText("")
            self.btn_create.setEnabled(False)
            return

        target_exists = (self.parent_dir / text.strip()).exists()
        if target_exists:
            valid = False
            msg = "A file or folder with this name already exists."

        self.btn_create.setEnabled(valid)
        self.error_label.setText(msg if not valid else "")

    def _on_create(self) -> None:
        self.filename = self.name_input.text().strip()
        self.accept()

    def get_filename(self) -> str:
        return self.filename
