"""Editor Manager component handling tabs, multiple files, and editor lifecycle."""
from pathlib import Path
from typing import Optional, List, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTabBar,
    QMessageBox,
    QFileDialog,
    QStackedWidget,
    QLabel,
    QPushButton,
    QFrame,
    QToolButton,
)

from utils.logger import get_logger
from utils.constants import APP_NAME, APP_VERSION
from editor.code_editor import CodeEditor
from dialogs.find_replace_dialog import FindReplaceWidget

logger = get_logger("editor_manager")


class EditorManager(QWidget):
    """Manages tabs, open documents, active editor state, and empty screen."""

    # Signals
    active_editor_changed = Signal(object)  # Optional[CodeEditor]
    cursor_position_changed = Signal(int, int)
    file_opened = Signal(Path)
    file_saved = Signal(Path)
    status_message_requested = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._untitled_counter: int = 1
        self._editors: List[CodeEditor] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Find & Replace Bar (collapsible at the top)
        self.find_replace_bar = FindReplaceWidget(self)
        self.find_replace_bar.hide()
        main_layout.addWidget(self.find_replace_bar)

        # Stacked widget: Index 0 = Welcome Screen, Index 1 = Tab Widget
        self.stack = QStackedWidget(self)

        # 1. Welcome Screen (when 0 tabs are open)
        self.welcome_screen = self._create_welcome_screen()
        self.stack.addWidget(self.welcome_screen)

        # 2. Tab Widget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        # Add a '+' button in the corner to create new tab
        new_tab_btn = QToolButton(self)
        new_tab_btn.setText("+")
        new_tab_btn.setToolTip("New File (Ctrl+N)")
        new_tab_btn.setStyleSheet(
            "QToolButton { background: transparent; border: none; color: #cccccc; "
            "font-size: 16px; font-weight: bold; padding: 2px 6px; margin: 2px; }"
            "QToolButton:hover { background-color: #3e3e42; border-radius: 3px; color: #ffffff; }"
        )
        new_tab_btn.clicked.connect(lambda: self.new_file())
        self.tab_widget.setCornerWidget(new_tab_btn, Qt.Corner.TopRightCorner)

        self.stack.addWidget(self.tab_widget)
        main_layout.addWidget(self.stack)

        self._update_stack_view()

    def _create_welcome_screen(self) -> QWidget:
        """Create a modern welcoming empty state when no files are open."""
        welcome = QWidget(self)
        layout = QVBoxLayout(welcome)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        title = QLabel(f"Welcome to {APP_NAME}")
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #ffffff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Modular Python IDE MVP — Phase 2 Code Editor")
        subtitle.setStyleSheet("font-size: 14px; color: #888888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #252526; border: 1px solid #333333; "
            "border-radius: 8px; padding: 24px; min-width: 380px; }"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        prompt = QLabel("Quick Actions:")
        prompt.setStyleSheet("font-size: 13px; font-weight: 600; color: #007acc;")
        card_layout.addWidget(prompt)

        btn_new = QPushButton("New Python File  (Ctrl+N)")
        btn_new.clicked.connect(lambda: self.new_file())
        card_layout.addWidget(btn_new)

        btn_open = QPushButton("Open File...  (Ctrl+O)")
        btn_open.clicked.connect(self.open_file_dialog)
        card_layout.addWidget(btn_open)

        info = QLabel(
            "• Powered by QScintilla with Python syntax highlighting.\n"
            "• Press Ctrl+S to save, Ctrl+W to close tab, Ctrl+F to find.\n"
            "• Open multiple files side-by-side with tab navigation."
        )
        info.setStyleSheet("color: #aaaaaa; font-size: 12px; line-height: 1.5;")
        card_layout.addWidget(info)

        layout.addWidget(card)
        return welcome

    def _update_stack_view(self) -> None:
        """Switch between welcome screen and tab widget based on open tab count."""
        if self.tab_widget.count() == 0:
            self.stack.setCurrentIndex(0)
            self.find_replace_bar.hide()
            self.active_editor_changed.emit(None)
        else:
            self.stack.setCurrentIndex(1)
            active = self.get_current_editor()
            self.active_editor_changed.emit(active)
            self.find_replace_bar.set_active_editor(active)

    def new_file(self, title_prefix: str = "Untitled") -> CodeEditor:
        """Create a new untitled file in a tab."""
        editor = CodeEditor(parent=self)
        title = f"{title_prefix}-{self._untitled_counter}.py"
        self._untitled_counter += 1

        editor.modification_changed.connect(lambda mod, ed=editor: self._on_editor_modified(ed, mod))
        editor.cursor_position_changed.connect(self.cursor_position_changed.emit)
        editor.file_saved.connect(lambda path, ed=editor: self._on_editor_saved(ed, path))

        index = self.tab_widget.addTab(editor, title)
        self.tab_widget.setTabToolTip(index, title)
        self.tab_widget.setCurrentIndex(index)
        self._editors.append(editor)

        self._update_stack_view()
        self.status_message_requested.emit(f"Created new file: {title}")
        logger.info("Created new file tab: %s", title)
        return editor

    def open_file_dialog(self) -> Optional[CodeEditor]:
        """Show file picker and open chosen file."""
        chosen_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Python Files (*.py);;All Files (*.*)",
        )
        if chosen_file:
            return self.open_file(Path(chosen_file))
        return None

    def open_file(self, file_path: Path) -> Optional[CodeEditor]:
        """Open a file or activate its existing tab if already opened."""
        p = Path(file_path).resolve()
        if not p.is_file():
            logger.warning("Attempted to open non-existent file: %s", p)
            QMessageBox.critical(self, "Error", f"File does not exist:\n{p}")
            return None

        # Check if already open
        existing_editor = self.find_editor_by_path(p)
        if existing_editor:
            index = self.tab_widget.indexOf(existing_editor)
            if index != -1:
                self.tab_widget.setCurrentIndex(index)
                self.status_message_requested.emit(f"Switched to: {p.name}")
                return existing_editor

        # Create new tab for file
        editor = CodeEditor(file_path=p, parent=self)
        if not editor.file_path:
            return None

        editor.modification_changed.connect(lambda mod, ed=editor: self._on_editor_modified(ed, mod))
        editor.cursor_position_changed.connect(self.cursor_position_changed.emit)
        editor.file_saved.connect(lambda saved_path, ed=editor: self._on_editor_saved(ed, saved_path))

        index = self.tab_widget.addTab(editor, p.name)
        self.tab_widget.setTabToolTip(index, str(p))
        self.tab_widget.setCurrentIndex(index)
        self._editors.append(editor)

        self._update_stack_view()
        self.file_opened.emit(p)
        self.status_message_requested.emit(f"Opened: {p.name}")
        logger.info("Opened file in editor: %s", p)
        return editor

    def save_current_file(self) -> bool:
        """Save the active editor file."""
        editor = self.get_current_editor()
        if not editor:
            return False

        if not editor.file_path:
            return self.save_file_as(editor)

        success = editor.save_file()
        if success:
            self._update_tab_title(editor)
            self.status_message_requested.emit(f"Saved: {editor.file_path.name}")
        return success

    def save_file_as(self, editor: Optional[CodeEditor] = None) -> bool:
        """Prompt user for target file path and save."""
        target_editor = editor or self.get_current_editor()
        if not target_editor:
            return False

        initial_name = str(target_editor.file_path) if target_editor.file_path else "untitled.py"
        chosen_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            initial_name,
            "Python Files (*.py);;All Files (*.*)",
        )
        if not chosen_path:
            return False

        p = Path(chosen_path).resolve()
        success = target_editor.save_file(p)
        if success:
            self._update_tab_title(target_editor)
            self.file_saved.emit(p)
            self.status_message_requested.emit(f"Saved: {p.name}")
        return success

    def close_tab(self, index: int) -> bool:
        """Close tab at index with confirmation if unsaved."""
        widget = self.tab_widget.widget(index)
        if not isinstance(widget, CodeEditor):
            return True

        if widget.is_modified():
            file_label = widget.get_file_name()
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"Do you want to save changes to '{file_label}' before closing?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )

            if reply == QMessageBox.StandardButton.Save:
                saved = self.save_file_as(widget) if not widget.file_path else widget.save_file()
                if not saved:
                    return False
            elif reply == QMessageBox.StandardButton.Cancel:
                return False

        # Remove tab
        self.tab_widget.removeTab(index)
        if widget in self._editors:
            self._editors.remove(widget)
        widget.deleteLater()

        self._update_stack_view()
        logger.info("Closed editor tab at index %d", index)
        return True

    def close_current_tab(self) -> bool:
        """Close the currently active tab."""
        current_idx = self.tab_widget.currentIndex()
        if current_idx != -1:
            return self.close_tab(current_idx)
        return True

    def close_all_tabs(self) -> bool:
        """Close all open tabs prompting for each unsaved file."""
        while self.tab_widget.count() > 0:
            success = self.close_tab(0)
            if not success:
                return False
        return True

    def get_current_editor(self) -> Optional[CodeEditor]:
        """Return the active CodeEditor instance."""
        widget = self.tab_widget.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None

    def find_editor_by_path(self, path: Path) -> Optional[CodeEditor]:
        """Find an open CodeEditor matching given path."""
        p_resolved = path.resolve()
        for ed in self._editors:
            if ed.file_path and ed.file_path.resolve() == p_resolved:
                return ed
        return None

    def has_unsaved_changes(self) -> bool:
        """Return True if any open editor has unsaved changes."""
        return any(ed.is_modified() for ed in self._editors)

    # Slots
    def _on_tab_changed(self, index: int) -> None:
        """Handle active tab change."""
        self._update_stack_view()
        active = self.get_current_editor()
        if active:
            line, col = active.get_cursor_position()
            self.cursor_position_changed.emit(line, col)
            self.status_message_requested.emit(f"Active: {active.get_file_name()}")

    def _on_editor_modified(self, editor: CodeEditor, modified: bool) -> None:
        """Update tab title when modified status changes."""
        self._update_tab_title(editor)

    def _on_editor_saved(self, editor: CodeEditor, path: Path) -> None:
        """Update tab title and tooltip on file save."""
        self._update_tab_title(editor)
        self.file_saved.emit(path)

    def _update_tab_title(self, editor: CodeEditor) -> None:
        """Set tab title with modified asterisk indicator."""
        index = self.tab_widget.indexOf(editor)
        if index != -1:
            name = editor.get_file_name()
            prefix = "* " if editor.is_modified() else ""
            self.tab_widget.setTabText(index, f"{prefix}{name}")
            if editor.file_path:
                self.tab_widget.setTabToolTip(index, str(editor.file_path))
