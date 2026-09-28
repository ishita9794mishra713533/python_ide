"""Dark theme stylesheet and UI theme definitions for SmartIDE."""

DARK_THEME_QSS = """
/* Global Application Styles */
QWidget {
    background-color: #1e1e1e;
    color: #cccccc;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", sans-serif;
    font-size: 13px;
    selection-background-color: #04395e;
    selection-color: #ffffff;
}

/* Main Window & Central Container */
QMainWindow {
    background-color: #1e1e1e;
}

QMainWindow::separator {
    background: #2b2b2b;
    width: 3px;
    height: 3px;
}

QMainWindow::separator:hover {
    background: #007acc;
}

/* Menu Bar & Menus */
QMenuBar {
    background-color: #2d2d2d;
    color: #cccccc;
    border-bottom: 1px solid #3c3c3c;
    padding: 2px 6px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #3e3e42;
    color: #ffffff;
}

QMenuBar::item:pressed {
    background-color: #094771;
    color: #ffffff;
}

QMenu {
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #454545;
    padding: 4px;
    border-radius: 4px;
}

QMenu::item {
    padding: 6px 28px 6px 20px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #094771;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: #3e3e42;
    margin: 4px 6px;
}

/* ToolBar */
QToolBar {
    background-color: #252526;
    border-bottom: 1px solid #333333;
    spacing: 6px;
    padding: 4px 8px;
}

QToolButton {
    background-color: transparent;
    color: #cccccc;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px 8px;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #3e3e42;
    color: #ffffff;
    border: 1px solid #4f4f54;
}

QToolButton:pressed {
    background-color: #007acc;
    color: #ffffff;
    border: 1px solid #005a9e;
}

/* Dock Widgets */
QDockWidget {
    color: #ffffff;
    font-weight: 600;
    titlebar-close-icon: url(none);
    titlebar-normal-icon: url(none);
}

QDockWidget::title {
    background-color: #252526;
    border-bottom: 1px solid #333333;
    text-align: left;
    padding: 6px 10px;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    color: #969696;
}

QDockWidget::title:hover {
    color: #ffffff;
}

/* Tree View (File Explorer) */
QTreeView {
    background-color: #252526;
    color: #cccccc;
    border: none;
    outline: none;
    show-decoration-selected: 1;
}

QTreeView::item {
    padding: 4px 6px;
    border-radius: 3px;
    border: none;
}

QTreeView::item:hover {
    background-color: #2a2d2e;
    color: #ffffff;
}

QTreeView::item:selected {
    background-color: #37373d;
    color: #ffffff;
}

QTreeView::item:selected:active {
    background-color: #094771;
    color: #ffffff;
}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
    border-image: none;
}

QHeaderView::section {
    background-color: #252526;
    color: #858585;
    padding: 4px 8px;
    border: none;
    border-bottom: 1px solid #333333;
    font-weight: 600;
    font-size: 11px;
}

/* Status Bar */
QStatusBar {
    background-color: #007acc;
    color: #ffffff;
    border-top: 1px solid #005a9e;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
    padding: 2px 8px;
}

QStatusBar QLabel {
    color: #ffffff;
    font-weight: 500;
    background: transparent;
}

/* Tab Widget (Editor Tabs) */
QTabWidget::pane {
    border: 1px solid #2d2d2d;
    background-color: #1e1e1e;
    top: -1px;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #969696;
    padding: 7px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid #252526;
    border-bottom: none;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #ffffff;
    border-top: 2px solid #007acc;
}

QTabBar::tab:hover:!selected {
    background-color: #353535;
    color: #d4d4d4;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #424242;
    min-height: 24px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #686868;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #424242;
    min-width: 24px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #686868;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    width: 0px;
}

/* Buttons */
QPushButton {
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #1177bb;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1177bb;
}

QPushButton:pressed {
    background-color: #094771;
}

QPushButton:disabled {
    background-color: #333333;
    color: #666666;
    border: 1px solid #444444;
}

/* Line Edit / Input */
QLineEdit {
    background-color: #3c3c3c;
    color: #cccccc;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 5px 8px;
}

QLineEdit:focus {
    border: 1px solid #007acc;
    background-color: #333333;
}

/* Tooltip */
QToolTip {
    background-color: #252526;
    color: #ffffff;
    border: 1px solid #454545;
    padding: 4px 8px;
    border-radius: 3px;
}
"""


def apply_dark_theme(app) -> None:
    """Apply the professional dark theme stylesheet to the QApplication."""
    app.setStyleSheet(DARK_THEME_QSS)


