"""Code Editor component implementing QScintilla with professional dark theme."""
import sys
from pathlib import Path
from typing import Optional, Tuple, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QMessageBox,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QWindow,
    QTextCursor,
    QTextDocument,
)

from utils.logger import get_logger
from editor.syntax_highlighter import (
    HAS_QSCI,
    DARK_THEME_COLORS,
    configure_qsci_python_lexer,
    PythonSyntaxHighlighter,
)

if HAS_QSCI:
    from PyQt6.Qsci import QsciScintilla, QsciLexerPython
    from PyQt6.QtGui import QColor as PQColor

logger = get_logger("code_editor")


class CodeEditor(QWidget):
    """High-performance Python Code Editor wrapping QScintilla."""

    # Signals
    modification_changed = Signal(bool)
    cursor_position_changed = Signal(int, int)
    file_saved = Signal(Path)

    def __init__(self, file_path: Optional[Path] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.file_path: Optional[Path] = file_path
        self._is_modified: bool = False
        self._qsci_scintilla: Optional[Any] = None
        self._plain_text_edit: Optional[QPlainTextEdit] = None
        self._using_qsci: bool = HAS_QSCI

        self._setup_ui()
        if self.file_path:
            self.load_file(self.file_path)

    def _setup_ui(self) -> None:
        """Initialize the editor layout and editor engine."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if self._using_qsci:
            try:
                self._setup_qsci_editor(layout)
                return
            except Exception as e:
                logger.error("Failed to initialize QScintilla editor, falling back to native editor: %s", e)
                self._using_qsci = False

        # Fallback to PySide6 native editor
        self._setup_native_editor(layout)

    def _setup_qsci_editor(self, layout: QVBoxLayout) -> None:
        """Configure QScintilla with line numbers, caret highlighting, and Python lexer."""
        sci = QsciScintilla()
        self._qsci_scintilla = sci

        # UTF-8 encoding
        sci.setUtf8(True)

        # Python Lexer with dark theme
        self.lexer = QsciLexerPython(sci)
        configure_qsci_python_lexer(self.lexer)
        sci.setLexer(self.lexer)

        # Line numbers margin (Margin 0)
        sci.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        sci.setMarginWidth(0, "0000")
        sci.setMarginsForegroundColor(PQColor(DARK_THEME_COLORS["line_number_fg"]))
        sci.setMarginsBackgroundColor(PQColor(DARK_THEME_COLORS["line_number_bg"]))
        sci.setMarginLineNumbers(0, True)

        # Code folding margin (Margin 1)
        sci.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle, 1)
        sci.setFoldMarginColors(
            PQColor(DARK_THEME_COLORS["fold_margin_bg"]),
            PQColor(DARK_THEME_COLORS["fold_margin_bg"]),
        )

        # Current line highlighting
        sci.setCaretLineVisible(True)
        sci.setCaretLineBackgroundColor(PQColor(DARK_THEME_COLORS["caret_line"]))

        # Caret appearance
        sci.setCaretForegroundColor(PQColor(DARK_THEME_COLORS["caret"]))
        sci.setCaretWidth(2)

        # Indentation & Tabs
        sci.setTabWidth(4)
        sci.setIndentationsUseTabs(False)
        sci.setAutoIndent(True)
        sci.setIndentationGuides(True)
        sci.setIndentationGuidesForegroundColor(PQColor(DARK_THEME_COLORS["indent_guide"]))

        # Selection colors
        sci.setSelectionBackgroundColor(PQColor(DARK_THEME_COLORS["selection"]))
        sci.setSelectionForegroundColor(PQColor("#ffffff"))

        # Base Font
        base_font = QFont("Consolas", 11)
        base_font.setFixedPitch(True)

        # Connect signals
        sci.modificationChanged.connect(self._on_modification_changed)
        sci.cursorPositionChanged.connect(self._on_qsci_cursor_changed)

        # Wrap in PySide6 container
        win = QWindow.fromWinId(int(sci.winId()))
        container = QWidget.createWindowContainer(win, self)
        layout.addWidget(container)
        logger.info("QScintilla editor initialized successfully.")

    def _setup_native_editor(self, layout: QVBoxLayout) -> None:
        """Configure PySide6 QPlainTextEdit with syntax highlighting fallback."""
        self._plain_text_edit = QPlainTextEdit(self)
        self._plain_text_edit.setStyleSheet(
            f"QPlainTextEdit {{ background-color: {DARK_THEME_COLORS['background']}; "
            f"color: {DARK_THEME_COLORS['foreground']}; font-family: 'Consolas'; font-size: 14px; "
            f"selection-background-color: {DARK_THEME_COLORS['selection']}; border: none; }}"
        )
        self.highlighter = PythonSyntaxHighlighter(self._plain_text_edit.document())

        self._plain_text_edit.textChanged.connect(lambda: self._on_modification_changed(True))
        self._plain_text_edit.cursorPositionChanged.connect(self._on_native_cursor_changed)

        layout.addWidget(self._plain_text_edit)
        logger.info("Native QPlainTextEdit editor initialized as fallback.")

    def get_text(self) -> str:
        """Retrieve full text from the editor."""
        if self._using_qsci and self._qsci_scintilla:
            return self._qsci_scintilla.text()
        elif self._plain_text_edit:
            return self._plain_text_edit.toPlainText()
        return ""

    def set_text(self, text: str) -> None:
        """Set full text in the editor."""
        if self._using_qsci and self._qsci_scintilla:
            self._qsci_scintilla.setText(text)
            self._qsci_scintilla.setModified(False)
        elif self._plain_text_edit:
            self._plain_text_edit.setPlainText(text)
            self._plain_text_edit.document().setModified(False)
        self.set_modified(False)

    def load_file(self, path: Path) -> bool:
        """Load file contents into editor using UTF-8."""
        p = Path(path).resolve()
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            self.set_text(content)
            self.file_path = p
            self.set_modified(False)
            logger.info("Loaded file successfully: %s", p)
            return True
        except UnicodeDecodeError:
            # Fallback with error handling
            try:
                with open(p, "r", encoding="latin-1") as f:
                    content = f.read()
                self.set_text(content)
                self.file_path = p
                self.set_modified(False)
                return True
            except Exception as e:
                logger.error("Failed to load file %s: %s", p, e)
                return False
        except Exception as e:
            logger.error("Error reading file %s: %s", p, e)
            return False

    def save_file(self, target_path: Optional[Path] = None) -> bool:
        """Save editor text to filesystem."""
        dest = target_path or self.file_path
        if not dest:
            logger.warning("Attempted to save file without path.")
            return False

        dest = Path(dest).resolve()
        try:
            # Ensure parent directories exist
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(self.get_text())

            self.file_path = dest
            self.set_modified(False)
            if self._using_qsci and self._qsci_scintilla:
                self._qsci_scintilla.setModified(False)
            elif self._plain_text_edit:
                self._plain_text_edit.document().setModified(False)

            logger.info("Saved file successfully: %s", dest)
            self.file_saved.emit(dest)
            return True
        except Exception as e:
            logger.error("Error saving file to %s: %s", dest, e)
            QMessageBox.critical(self, "Save Error", f"Could not save file to:\n{dest}\n\nError: {e}")
            return False

    def is_modified(self) -> bool:
        """Check if editor has unsaved changes."""
        return self._is_modified

    def set_modified(self, modified: bool) -> None:
        """Set modification state and emit signal."""
        if self._is_modified != modified:
            self._is_modified = modified
            self.modification_changed.emit(modified)

    def get_file_name(self) -> str:
        """Return the base file name or Untitled."""
        return self.file_path.name if self.file_path else "Untitled"

    def get_cursor_position(self) -> Tuple[int, int]:
        """Return 1-indexed (line, column)."""
        if self._using_qsci and self._qsci_scintilla:
            line, col = self._qsci_scintilla.getCursorPosition()
            return line + 1, col + 1
        elif self._plain_text_edit:
            cursor = self._plain_text_edit.textCursor()
            return cursor.blockNumber() + 1, cursor.columnNumber() + 1
        return 1, 1

    # Editor Operations
    def undo(self) -> None:
        if self._using_qsci and self._qsci_scintilla:
            self._qsci_scintilla.undo()
        elif self._plain_text_edit:
            self._plain_text_edit.undo()

    def redo(self) -> None:
        if self._using_qsci and self._qsci_scintilla:
            self._qsci_scintilla.redo()
        elif self._plain_text_edit:
            self._plain_text_edit.redo()

    def cut(self) -> None:
        if self._using_qsci and self._qsci_scintilla:
            self._qsci_scintilla.cut()
        elif self._plain_text_edit:
            self._plain_text_edit.cut()

    def copy(self) -> None:
        if self._using_qsci and self._qsci_scintilla:
            self._qsci_scintilla.copy()
        elif self._plain_text_edit:
            self._plain_text_edit.copy()

    def paste(self) -> None:
        if self._using_qsci and self._qsci_scintilla:
            self._qsci_scintilla.paste()
        elif self._plain_text_edit:
            self._plain_text_edit.paste()

    def find_text(self, expr: str, forward: bool = True, case_sensitive: bool = False, whole_word: bool = False) -> bool:
        """Search for text in editor."""
        if not expr:
            return False

        if self._using_qsci and self._qsci_scintilla:
            return self._qsci_scintilla.findFirst(
                expr,
                False,  # re
                case_sensitive,
                whole_word,
                True,   # wrap
                forward
            )
        elif self._plain_text_edit:
            flags = QTextDocument.FindFlag(0)
            if not forward:
                flags |= QTextDocument.FindFlag.FindBackward
            if case_sensitive:
                flags |= QTextDocument.FindFlag.FindCaseSensitively
            if whole_word:
                flags |= QTextDocument.FindFlag.FindWholeWords
            found = self._plain_text_edit.find(expr, flags)
            return found
        return False

    def replace_text(self, expr: str, replacement: str, forward: bool = True, case_sensitive: bool = False, whole_word: bool = False) -> bool:
        """Replace the current selection or find next and replace."""
        if self._using_qsci and self._qsci_scintilla:
            if self._qsci_scintilla.hasSelectedText() and (
                (case_sensitive and self._qsci_scintilla.selectedText() == expr)
                or (not case_sensitive and self._qsci_scintilla.selectedText().lower() == expr.lower())
            ):
                self._qsci_scintilla.replace(replacement)
                self.find_text(expr, forward, case_sensitive, whole_word)
                return True
            else:
                if self.find_text(expr, forward, case_sensitive, whole_word):
                    self._qsci_scintilla.replace(replacement)
                    return True
                return False
        elif self._plain_text_edit:
            cursor = self._plain_text_edit.textCursor()
            if cursor.hasSelection():
                cursor.insertText(replacement)
                self.find_text(expr, forward, case_sensitive, whole_word)
                return True
            elif self.find_text(expr, forward, case_sensitive, whole_word):
                cursor = self._plain_text_edit.textCursor()
                cursor.insertText(replacement)
                return True
        return False

    def replace_all(self, expr: str, replacement: str, case_sensitive: bool = False, whole_word: bool = False) -> int:
        """Replace all occurrences in the entire document."""
        if not expr:
            return 0
        count = 0
        current_text = self.get_text()
        if case_sensitive:
            count = current_text.count(expr)
            new_text = current_text.replace(expr, replacement)
        else:
            import re
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.escape(expr)
            if whole_word:
                pattern = rf"\b{pattern}\b"
            new_text, count = re.subn(pattern, replacement, current_text, flags=flags)

        if count > 0:
            self.set_text(new_text)
            self.set_modified(True)
        return count

    # Internal Slots
    def _on_modification_changed(self, modified: bool) -> None:
        self.set_modified(modified)

    def _on_qsci_cursor_changed(self, line: int, col: int) -> None:
        self.cursor_position_changed.emit(line + 1, col + 1)

    def _on_native_cursor_changed(self) -> None:
        line, col = self.get_cursor_position()
        self.cursor_position_changed.emit(line, col)
