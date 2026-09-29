from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QLabel,
    QToolButton,
    QDialog,
)

if TYPE_CHECKING:
    from editor.code_editor import CodeEditor


class FindReplaceWidget(QFrame):
    """Sleek inline Find & Replace bar."""

    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_editor: Optional[CodeEditor] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setObjectName("findReplaceBar")
        self.setStyleSheet(
            "QFrame#findReplaceBar { background-color: #252526; border: 1px solid #454545; "
            "border-radius: 6px; padding: 6px; }"
            "QLineEdit { background-color: #3c3c3c; color: #ffffff; border: 1px solid #555555; "
            "border-radius: 3px; padding: 4px 8px; min-width: 180px; }"
            "QLineEdit:focus { border: 1px solid #007acc; }"
            "QPushButton { background-color: #333333; color: #cccccc; border: 1px solid #555555; "
            "border-radius: 3px; padding: 3px 8px; font-size: 11px; }"
            "QPushButton:hover { background-color: #444444; color: #ffffff; }"
            "QToolButton { background: transparent; border: none; color: #888888; font-weight: bold; }"
            "QToolButton:hover { color: #ffffff; }"
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # Row 1: Find
        row1 = QHBoxLayout()
        row1.setSpacing(6)

        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Find...")
        self.find_input.returnPressed.connect(self.find_next)
        row1.addWidget(self.find_input)

        self.btn_find_prev = QPushButton("▲ Prev")
        self.btn_find_prev.clicked.connect(self.find_prev)
        row1.addWidget(self.btn_find_prev)

        self.btn_find_next = QPushButton("▼ Next")
        self.btn_find_next.clicked.connect(self.find_next)
        row1.addWidget(self.btn_find_next)

        self.chk_case = QCheckBox("Aa")
        self.chk_case.setToolTip("Match Case")
        row1.addWidget(self.chk_case)

        self.chk_word = QCheckBox(r"\b")
        self.chk_word.setToolTip("Match Whole Word")
        row1.addWidget(self.chk_word)

        btn_close = QToolButton()
        btn_close.setText("✕")
        btn_close.setToolTip("Close (Esc)")
        btn_close.clicked.connect(self.hide_bar)
        row1.addWidget(btn_close)

        main_layout.addLayout(row1)

        # Row 2: Replace
        self.row2_widget = QFrame()
        row2 = QHBoxLayout(self.row2_widget)
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(6)

        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        self.replace_input.returnPressed.connect(self.replace_current)
        row2.addWidget(self.replace_input)

        self.btn_replace = QPushButton("Replace")
        self.btn_replace.clicked.connect(self.replace_current)
        row2.addWidget(self.btn_replace)

        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.clicked.connect(self.replace_all)
        row2.addWidget(self.btn_replace_all)

        main_layout.addWidget(self.row2_widget)

    def set_active_editor(self, editor: Optional[CodeEditor]) -> None:
        """Bind the Find & Replace bar to current active editor."""
        self.active_editor = editor

    def show_find(self, editor: Optional[CodeEditor] = None) -> None:
        """Open bar in Find mode."""
        if editor:
            self.set_active_editor(editor)
        self.row2_widget.hide()
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def show_replace(self, editor: Optional[CodeEditor] = None) -> None:
        """Open bar in Replace mode."""
        if editor:
            self.set_active_editor(editor)
        self.row2_widget.show()
        self.show()
        self.find_input.setFocus()
        self.find_input.selectAll()

    def hide_bar(self) -> None:
        """Hide the Find & Replace bar and return focus."""
        self.hide()
        self.closed.emit()
        if self.active_editor:
            self.active_editor.setFocus()

    def keyPressEvent(self, event) -> None:
        """Handle Escape key to close."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_bar()
        else:
            super().keyPressEvent(event)

    def find_next(self) -> bool:
        if not self.active_editor:
            return False
        return self.active_editor.find_text(
            self.find_input.text(),
            forward=True,
            case_sensitive=self.chk_case.isChecked(),
            whole_word=self.chk_word.isChecked(),
        )

    def find_prev(self) -> bool:
        if not self.active_editor:
            return False
        return self.active_editor.find_text(
            self.find_input.text(),
            forward=False,
            case_sensitive=self.chk_case.isChecked(),
            whole_word=self.chk_word.isChecked(),
        )

    def replace_current(self) -> bool:
        if not self.active_editor:
            return False
        return self.active_editor.replace_text(
            self.find_input.text(),
            self.replace_input.text(),
            forward=True,
            case_sensitive=self.chk_case.isChecked(),
            whole_word=self.chk_word.isChecked(),
        )

    def replace_all(self) -> int:
        if not self.active_editor:
            return 0
        return self.active_editor.replace_all(
            self.find_input.text(),
            self.replace_input.text(),
            case_sensitive=self.chk_case.isChecked(),
            whole_word=self.chk_word.isChecked(),
        )


class FindReplaceDialog(QDialog):
    """Find and Replace modal/modeless dialog wrapper."""

    def __init__(self, editor_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.resize(500, 180)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.widget = FindReplaceWidget(self)
        self.widget.closed.connect(self.close)
        layout.addWidget(self.widget)
        self.editor_manager = editor_manager

    def show(self):
        ed = self.editor_manager.current_editor()
        if ed:
            self.widget.set_active_editor(ed)
        super().show()
