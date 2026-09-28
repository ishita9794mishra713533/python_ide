"""Code editor package for SmartIDE."""
from editor.code_editor import CodeEditor
from editor.editor_manager import EditorManager
from editor.syntax_highlighter import configure_qsci_python_lexer

__all__ = ["CodeEditor", "EditorManager", "configure_qsci_python_lexer"]