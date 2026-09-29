"""
Code Editor component for SmartIDE using PySide6 QPlainTextEdit.
Features:
- Line number gutter margin
- Active line highlighting
- Python syntax highlighting
- Auto-indentation & 4-space tab handling
- Find & replace operations
- Live cursor position tracking
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtCore import Qt, Signal, QRect, QSize
from PySide6.QtWidgets import (
    QWidget,
    QPlainTextEdit,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QTextCursor,
    QTextDocument,
    QTextFormat,
)

from utils.logger import get_logger
from editor.syntax_highlighter import DARK_THEME_COLORS, PythonSyntaxHighlighter

logger = get_logger("code_editor")


class LineNumberArea(QWidget):
    """Left gutter displaying line numbers for CodeEditor."""

    def __init__(self, editor: CodeEditor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Professional, high-performance Python code editor widget."""

    modification_changed = Signal(bool)
    cursor_position_changed = Signal(int, int)
    file_saved = Signal(Path)

    def __init__(self, file_path: Optional[Path] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.file_path: Optional[Path] = file_path
        self._is_modified: bool = False
        self._using_qsci: bool = False  # Compatibility flag

        self._setup_editor()

        # Line number area
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._on_cursor_changed)
        self.textChanged.connect(self._on_text_changed)

        self._update_line_number_area_width(0)
        self._highlight_current_line()

        # Syntax highlighter
        self.highlighter = PythonSyntaxHighlighter(self.document())

        if self.file_path:
            self.load_file(self.file_path)

    # -------------------------------------------------------------------------
    # Styling & Setup
    # -------------------------------------------------------------------------
    def _setup_editor(self) -> None:
        """Apply editor font, tab width, and palette."""
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        self.setFont(font)

        # 4 spaces tab stop
        metrics = self.fontMetrics()
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))

        self.setStyleSheet(
            f"QPlainTextEdit {{ "
            f"background-color: {DARK_THEME_COLORS['background']}; "
            f"color: {DARK_THEME_COLORS['foreground']}; "
            f"selection-background-color: {DARK_THEME_COLORS['selection']}; "
            f"selection-color: #ffffff; "
            f"border: none; "
            f"}}"
        )
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    # -------------------------------------------------------------------------
    # Line Number Margin
    # -------------------------------------------------------------------------
    def line_number_area_width(self) -> int:
        digits = max(1, len(str(max(1, self.blockCount()))))
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def _update_line_number_area_width(self, _) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def line_number_area_paint_event(self, event) -> None:
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(DARK_THEME_COLORS["line_number_bg"]))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        painter.setPen(QColor(DARK_THEME_COLORS["line_number_fg"]))
        font = self.font()
        font.setPointSize(max(8, self.font().pointSize() - 1))
        painter.setFont(font)

        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                num_str = str(block_number + 1)
                if block_number == current_line:
                    painter.setPen(QColor("#ffffff"))
                else:
                    painter.setPen(QColor(DARK_THEME_COLORS["line_number_fg"]))

                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width() - 8,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    num_str,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    # -------------------------------------------------------------------------
    # Active Line Highlight
    # -------------------------------------------------------------------------
    def _highlight_current_line(self) -> None:
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(DARK_THEME_COLORS["caret_line"]))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def _on_cursor_changed(self) -> None:
        self._highlight_current_line()
        self.line_number_area.update()
        line, col = self.get_cursor_position()
        self.cursor_position_changed.emit(line, col)

    def _on_text_changed(self) -> None:
        if not self._is_modified:
            self.set_modified(True)

    # -------------------------------------------------------------------------
    # Keyboard Handling (Indentation, Auto-Indent, 4 Spaces)
    # -------------------------------------------------------------------------
    def keyPressEvent(self, event) -> None:
        # Tab -> 4 spaces
        if event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            if cursor.hasSelection():
                # Indent selected lines
                self._indent_selection(forward=True)
            else:
                self.insertPlainText("    ")
            return

        # Shift + Tab -> Unindent 4 spaces
        if event.key() == Qt.Key.Key_Backtab:
            self._indent_selection(forward=False)
            return

        # Return / Enter -> Auto-indentation
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()
            block = cursor.block()
            line_text = block.text()
            
            # Count leading spaces
            match = re.match(r"^([ \t]*)", line_text)
            indent = match.group(1) if match else ""

            # If line ended with ':', add 4 more spaces
            stripped = line_text.rstrip()
            if stripped.endswith(":"):
                indent += "    "

            super().keyPressEvent(event)
            self.insertPlainText(indent)
            return

        super().keyPressEvent(event)

    def _indent_selection(self, forward: bool = True) -> None:
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(start)
        start_block = cursor.block().blockNumber()
        cursor.setPosition(end)
        end_block = cursor.block().blockNumber()

        cursor.beginEditBlock()
        for b_idx in range(start_block, end_block + 1):
            block = self.document().findBlockByNumber(b_idx)
            cur = QTextCursor(block)
            cur.movePosition(QTextCursor.MoveOperation.StartOfLine)
            if forward:
                cur.insertText("    ")
            else:
                text = block.text()
                if text.startswith("    "):
                    for _ in range(4):
                        cur.deleteChar()
                elif text.startswith("\t") or text.startswith(" "):
                    cur.deleteChar()
        cursor.endEditBlock()

    # -------------------------------------------------------------------------
    # Public API & Text Operations
    # -------------------------------------------------------------------------
    @property
    def language(self) -> str:
        if self.file_path:
            ext = self.file_path.suffix.lower()
            if ext in (".py", ".pyw"):
                return "python"
            elif ext == ".sql":
                return "sql"
            elif ext == ".json":
                return "json"
            elif ext == ".md":
                return "markdown"
        return "python"

    def get_text(self) -> str:
        return self.toPlainText()

    def set_text(self, text: str, mark_modified: Optional[bool] = None) -> None:
        self.setPlainText(text)
        if mark_modified is not None:
            self.set_modified(mark_modified)
        else:
            self.set_modified(True)

    def load_file(self, path: Path | str) -> bool:
        p = Path(path).resolve()
        try:
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            self.setPlainText(content)
            self.file_path = p
            self.set_modified(False)
            logger.info("Loaded file successfully: %s", p)
            return True
        except UnicodeDecodeError:
            try:
                with open(p, "r", encoding="latin-1") as f:
                    content = f.read()
                self.setPlainText(content)
                self.file_path = p
                self.set_modified(False)
                return True
            except Exception as e:
                logger.error("Failed to load file %s: %s", p, e)
                return False
        except Exception as e:
            logger.error("Error reading file %s: %s", p, e)
            return False

    def save_file(self, target_path: Optional[Path | str] = None) -> bool:
        dest = target_path or self.file_path
        if not dest:
            logger.warning("Attempted to save file without path.")
            return False

        dest = Path(dest).resolve()
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(self.toPlainText())

            self.file_path = dest
            self.set_modified(False)
            logger.info("Saved file successfully: %s", dest)
            self.file_saved.emit(dest)
            return True
        except Exception as e:
            logger.error("Error saving file to %s: %s", dest, e)
            QMessageBox.critical(self, "Save Error", f"Could not save file to:\n{dest}\n\nError: {e}")
            return False

    def is_modified(self) -> bool:
        return self._is_modified

    def set_modified(self, modified: bool) -> None:
        if self._is_modified != modified:
            self._is_modified = modified
            self.document().setModified(modified)
            self.modification_changed.emit(modified)

    def get_file_name(self) -> str:
        return self.file_path.name if self.file_path else "Untitled"

    def get_cursor_position(self) -> Tuple[int, int]:
        cursor = self.textCursor()
        return cursor.blockNumber() + 1, cursor.columnNumber() + 1

    def get_current_line(self) -> int:
        line, _ = self.get_cursor_position()
        return line

    def get_current_column(self) -> int:
        _, col = self.get_cursor_position()
        return col

    def select_all(self) -> None:
        self.selectAll()

    # -------------------------------------------------------------------------
    # Find & Replace
    # -------------------------------------------------------------------------
    def find_text(
        self,
        expr: str,
        forward: bool = True,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> bool:
        if not expr:
            return False

        flags = QTextDocument.FindFlag(0)
        if not forward:
            flags |= QTextDocument.FindFlag.FindBackward
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_word:
            flags |= QTextDocument.FindFlag.FindWholeWords

        found = self.find(expr, flags)
        if not found:
            # Wrap around search
            cursor = self.textCursor()
            if forward:
                cursor.movePosition(QTextCursor.MoveOperation.Start)
            else:
                cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            found = self.find(expr, flags)

        return found

    def replace_text(
        self,
        expr: str,
        replacement: str,
        forward: bool = True,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> bool:
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            matches = (selected == expr) if case_sensitive else (selected.lower() == expr.lower())
            if matches:
                cursor.insertText(replacement)
                self.find_text(expr, forward, case_sensitive, whole_word)
                return True

        if self.find_text(expr, forward, case_sensitive, whole_word):
            self.textCursor().insertText(replacement)
            return True

        return False

    def replace_all(
        self,
        expr: str,
        replacement: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> int:
        if not expr:
            return 0

        current_text = self.toPlainText()
        if case_sensitive:
            count = current_text.count(expr)
            new_text = current_text.replace(expr, replacement)
        else:
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.escape(expr)
            if whole_word:
                pattern = rf"\b{pattern}\b"
            new_text, count = re.subn(pattern, replacement, current_text, flags=flags)

        if count > 0:
            self.set_text(new_text)
            self.set_modified(True)

        return count
