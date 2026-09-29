"""Syntax highlighting configurations and styles for SmartIDE."""
from typing import Dict, Any
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtCore import QRegularExpression

try:
    from PyQt6.Qsci import QsciScintilla, QsciLexerPython
    from PyQt6.QtGui import QColor as PQColor, QFont as PQFont
    HAS_QSCI = True
except ImportError:
    HAS_QSCI = False

DARK_THEME_COLORS = {
    "background": "#1e1e1e",
    "foreground": "#d4d4d4",
    "caret": "#ffffff",
    "caret_line": "#282828",
    "selection": "#264f78",
    "line_number_fg": "#858585",
    "line_number_bg": "#252526",
    "fold_margin_bg": "#252526",
    "indent_guide": "#404040",
    "comment": "#6a9955",
    "keyword": "#569cd6",
    "string": "#ce9178",
    "number": "#b5cea8",
    "function": "#dcdcaa",
    "class_name": "#4ec9b0",
    "operator": "#d4d4d4",
    "decorator": "#c586c0",
    "unclosed_string": "#e06c75",
}


def configure_qsci_python_lexer(lexer: Any) -> None:
    """Configure QsciLexerPython with the professional dark theme."""
    if not HAS_QSCI or not isinstance(lexer, QsciLexerPython):
        return

    code_font = PQFont("Consolas", 11)
    code_font.setFixedPitch(True)
    lexer.setFont(code_font)

    lexer.setDefaultPaper(PQColor(DARK_THEME_COLORS["background"]))
    lexer.setDefaultColor(PQColor(DARK_THEME_COLORS["foreground"]))

    style_configs = {
        QsciLexerPython.Default: (DARK_THEME_COLORS["foreground"], False, False),
        QsciLexerPython.Comment: (DARK_THEME_COLORS["comment"], False, True),
        QsciLexerPython.CommentBlock: (DARK_THEME_COLORS["comment"], False, True),
        QsciLexerPython.Number: (DARK_THEME_COLORS["number"], False, False),
        QsciLexerPython.DoubleQuotedString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.SingleQuotedString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.DoubleQuotedFString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.SingleQuotedFString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.Keyword: (DARK_THEME_COLORS["keyword"], True, False),
        QsciLexerPython.TripleSingleQuotedString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.TripleDoubleQuotedString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.TripleSingleQuotedFString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.TripleDoubleQuotedFString: (DARK_THEME_COLORS["string"], False, False),
        QsciLexerPython.ClassName: (DARK_THEME_COLORS["class_name"], True, False),
        QsciLexerPython.FunctionMethodName: (DARK_THEME_COLORS["function"], False, False),
        QsciLexerPython.Operator: (DARK_THEME_COLORS["operator"], False, False),
        QsciLexerPython.Identifier: (DARK_THEME_COLORS["foreground"], False, False),
        QsciLexerPython.UnclosedString: (DARK_THEME_COLORS["unclosed_string"], False, False),
        QsciLexerPython.Decorator: (DARK_THEME_COLORS["decorator"], False, False),
    }

    for style_id, (hex_color, bold, italic) in style_configs.items():
        lexer.setColor(PQColor(hex_color), style_id)
        lexer.setPaper(PQColor(DARK_THEME_COLORS["background"]), style_id)
        f = PQFont("Consolas", 11)
        f.setFixedPitch(True)
        f.setBold(bold)
        f.setItalic(italic)
        lexer.setFont(f, style_id)


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    """Native PySide6 syntax highlighter for Python code (fallback & hybrid support)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(DARK_THEME_COLORS["keyword"]))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            r"\band\b", r"\bas\b", r"\bassert\b", r"\bbreak\b", r"\bclass\b",
            r"\bcontinue\b", r"\bdef\b", r"\bdel\b", r"\belif\b", r"\belse\b",
            r"\bexcept\b", r"\bfinally\b", r"\bfor\b", r"\bfrom\b", r"\bglobal\b",
            r"\bif\b", r"\bimport\b", r"\bin\b", r"\bis\b", r"\blambda\b",
            r"\bmatch\b", r"\bcase\b",
            r"\bnonlocal\b", r"\bnot\b", r"\bor\b", r"\bpass\b", r"\braise\b",
            r"\breturn\b", r"\btry\b", r"\bwhile\b", r"\bwith\b", r"\byield\b",
            r"\bTrue\b", r"\bFalse\b", r"\bNone\b", r"\basync\b", r"\bawait\b",
        ]
        for pattern in keywords:
            self._highlighting_rules.append((QRegularExpression(pattern), keyword_format))

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#4ec9b0"))
        builtins = [
            r"\bprint\b", r"\blen\b", r"\brange\b", r"\bint\b", r"\bstr\b",
            r"\bfloat\b", r"\blist\b", r"\bdict\b", r"\bset\b", r"\btuple\b",
            r"\bbool\b", r"\btype\b", r"\bisinstance\b", r"\benumerate\b",
            r"\bzip\b", r"\bopen\b", r"\bsuper\b", r"\binput\b", r"\bmap\b",
        ]
        for pattern in builtins:
            self._highlighting_rules.append((QRegularExpression(pattern), builtin_format))

        func_format = QTextCharFormat()
        func_format.setForeground(QColor(DARK_THEME_COLORS["function"]))
        self._highlighting_rules.append((QRegularExpression(r"\bdef\s+([A-Za-z_0-9]+)"), func_format))

        class_format = QTextCharFormat()
        class_format.setForeground(QColor(DARK_THEME_COLORS["class_name"]))
        class_format.setFontWeight(QFont.Weight.Bold)
        self._highlighting_rules.append((QRegularExpression(r"\bclass\s+([A-Za-z_0-9]+)"), class_format))

        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor(DARK_THEME_COLORS["decorator"]))
        self._highlighting_rules.append((QRegularExpression(r"@[A-Za-z_0-9.]+"), decorator_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(DARK_THEME_COLORS["number"]))
        self._highlighting_rules.append((QRegularExpression(r"\b[0-9]+(\.[0-9]+)?\b"), number_format))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(DARK_THEME_COLORS["string"]))
        self._highlighting_rules.append((QRegularExpression(r"\"[^\"]*\""), self.string_format))
        self._highlighting_rules.append((QRegularExpression(r"'[^']*'"), self.string_format))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(DARK_THEME_COLORS["comment"]))
        self.comment_format.setFontItalic(True)
        self._highlighting_rules.append((QRegularExpression(r"#[^\n]*"), self.comment_format))

    def highlightBlock(self, text: str) -> None:
        """Apply syntax highlighting to given block of text."""
        for pattern, fmt in self._highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
