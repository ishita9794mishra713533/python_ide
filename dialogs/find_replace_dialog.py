"""Find and Replace widget for SmartIDE editor."""
from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox
from PySide6.QtCore import Qt

class FindReplaceWidget(QWidget):
    """Find and replace bar embedded above the code editor."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.active_editor = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self.lbl_find = QLabel("Find:", self)
        self.txt_find = QLineEdit(self)
        self.txt_find.setPlaceholderText("Search string...")

        self.lbl_replace = QLabel("Replace:", self)
        self.txt_replace = QLineEdit(self)
        self.txt_replace.setPlaceholderText("Replacement string...")

        self.btn_next = QPushButton("Next", self)
        self.btn_prev = QPushButton("Prev", self)
        self.btn_replace = QPushButton("Replace", self)
        self.btn_replace_all = QPushButton("Replace All", self)
        self.btn_close = QPushButton("✕", self)
        self.btn_close.setFlat(True)
        self.btn_close.clicked.connect(self.hide)

        layout.addWidget(self.lbl_find)
        layout.addWidget(self.txt_find)
        layout.addWidget(self.lbl_replace)
        layout.addWidget(self.txt_replace)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_replace)
        layout.addWidget(self.btn_replace_all)
        layout.addWidget(self.btn_close)

    def set_active_editor(self, editor) -> None:
        """Set the active editor target for find and replace operations."""
        self.active_editor = editor
