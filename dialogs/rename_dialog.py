"""Modal dialog for renaming a file or directory."""
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



class RenameDialog(QDialog):
    """Dialog to prompt user for a new name for an existing file or directory."""

    def __init__(self, target_path: Path, parent=None):
        super().__init__(parent)
        self.target_path = Path(target_path).resolve()
        self.new_name: str = ""

        is_dir = self.target_path.is_dir()
        self.setWindowTitle("Rename Folder" if is_dir else "Rename File")
        self.setFixedSize(380, 160)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Current name label
        current_label = QLabel(f"Current: <b>{self.target_path.name}</b>")
        current_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(current_label)

        # Name label
        label = QLabel("New name:")
        label.setStyleSheet("font-weight: 500;")
        layout.addWidget(label)

        # Input
        self.name_input = QLineEdit(self)
        self.name_input.setText(self.target_path.name)
        self.name_input.textChanged.connect(self._validate_input)
        layout.addWidget(self.name_input)

        # Preselect filename without extension
        if self.target_path.is_file() and "." in self.target_path.name:
            stem_len = len(self.target_path.stem)
            self.name_input.setSelection(0, stem_len)
        else:
            self.name_input.selectAll()

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

        self.btn_rename = QPushButton("Rename", self)
        self.btn_rename.setEnabled(False)
        self.btn_rename.setDefault(True)
        self.btn_rename.clicked.connect(self._on_rename)
        btn_layout.addWidget(self.btn_rename)

        layout.addLayout(btn_layout)

    def _validate_input(self, text: str) -> None:
        clean = text.strip()
        if not clean or clean == self.target_path.name:
            self.error_label.setText("")
            self.btn_rename.setEnabled(False)
            return

        valid, msg = FileManager.validate_name(clean)
        destination = self.target_path.parent / clean
        if destination.exists():
            valid = False
            msg = f"An item named '{clean}' already exists."

        self.btn_rename.setEnabled(valid)
        self.error_label.setText(msg if not valid else "")

    def _on_rename(self) -> None:
        self.new_name = self.name_input.text().strip()
        self.accept()

    def get_new_name(self) -> str:
        return self.new_name
