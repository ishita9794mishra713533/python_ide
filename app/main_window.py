"""
SmartIDE - Main Application Window
Coordinates all components: Menu bar, Toolbar, File Explorer, Editor Manager,
Database Explorer, SQL Console, and Status Bar.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QProcess, Slot, QByteArray
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QDockWidget, QFileDialog, QMessageBox,
    QStatusBar, QLabel, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QHBoxLayout, QTabWidget, QSplitter
)

from app.settings import SettingsManager
from app.styles import DarkTheme, LightTheme
from utils.constants import APP_NAME, APP_VERSION
from utils.logger import get_logger
from explorer.file_explorer import FileExplorerWidget
from editor.editor_manager import EditorManager
from database.sqlite_manager import SQLiteManager
from database.database_explorer import DatabaseExplorer
from database.sql_console import SQLConsole
from database.table_viewer import TableViewerDialog
from dialogs.find_replace_dialog import FindReplaceDialog

logger = get_logger("MainWindow")


class MainWindow(QMainWindow):
    """The central application window for SmartIDE."""

    def __init__(self, initial_path: Optional[str] = None):
        super().__init__()
        self.settings = SettingsManager()
        self.db_manager = SQLiteManager()
        self.process: Optional[QProcess] = None
        self._find_replace_dialog: Optional[FindReplaceDialog] = None

        self._init_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._connect_signals()
        self._restore_state(initial_path)

        logger.info("MainWindow initialized successfully.")

    # -------------------------------------------------------------------------
    # UI Setup
    # -------------------------------------------------------------------------
    def _init_ui(self) -> None:
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1200, 800)

        # Central Widget: Editor Manager
        self.editor_manager = EditorManager(self)
        self.setCentralWidget(self.editor_manager)

        # Left Dock 1: File Explorer
        self.explorer_dock = QDockWidget("Project Explorer", self)
        self.explorer_dock.setObjectName("ProjectExplorerDock")
        self.explorer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.file_explorer = FileExplorerWidget(self)
        self.explorer_dock.setWidget(self.file_explorer)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.explorer_dock)

        # Left Dock 2: Database Explorer
        self.db_dock = QDockWidget("Database Explorer", self)
        self.db_dock.setObjectName("DatabaseExplorerDock")
        self.db_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.db_explorer = DatabaseExplorer(self.db_manager, self)
        self.db_dock.setWidget(self.db_explorer)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.db_dock)
        self.tabifyDockWidget(self.explorer_dock, self.db_dock)
        self.explorer_dock.raise_()

        # Bottom Dock: Output & SQL Console
        self.bottom_dock = QDockWidget("Terminal / Output & Console", self)
        self.bottom_dock.setObjectName("BottomOutputDock")
        self.bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)

        self.bottom_tabs = QTabWidget(self)
        
        # Execution Output Panel
        self.output_widget = QWidget()
        out_layout = QVBoxLayout(self.output_widget)
        out_layout.setContentsMargins(4, 4, 4, 4)
        
        out_btn_bar = QHBoxLayout()
        self.btn_clear_output = QPushButton("Clear Output")
        self.btn_stop_process = QPushButton("Stop Process")
        self.btn_stop_process.setEnabled(False)
        self.lbl_process_status = QLabel("Idle")
        out_btn_bar.addWidget(self.btn_clear_output)
        out_btn_bar.addWidget(self.btn_stop_process)
        out_btn_bar.addWidget(self.lbl_process_status)
        out_btn_bar.addStretch()

        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setFontFamily("Consolas, Courier New, monospace")

        out_layout.addLayout(out_btn_bar)
        out_layout.addWidget(self.txt_output)
        self.bottom_tabs.addTab(self.output_widget, "Execution Output")

        # SQL Console
        self.sql_console = SQLConsole(self.db_manager, self)
        self.bottom_tabs.addTab(self.sql_console, "SQL Console")

        self.bottom_dock.setWidget(self.bottom_tabs)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def _create_actions(self) -> None:
        # File Actions
        self.act_new_file = QAction("&New File", self)
        self.act_new_file.setShortcut(QKeySequence.StandardKey.New)
        self.act_new_file.setStatusTip("Create a new scratch file")
        self.act_new_file.triggered.connect(self._on_action_new_file)

        self.act_open_file = QAction("&Open File...", self)
        self.act_open_file.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open_file.setStatusTip("Open a file from disk")
        self.act_open_file.triggered.connect(self._on_action_open_file)

        self.act_open_folder = QAction("Open &Folder...", self)
        self.act_open_folder.setShortcut(QKeySequence("Ctrl+K, Ctrl+O"))
        self.act_open_folder.setStatusTip("Open a folder in the File Explorer")
        self.act_open_folder.triggered.connect(self._on_action_open_folder)

        self.act_save_file = QAction("&Save", self)
        self.act_save_file.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save_file.setStatusTip("Save the active document")
        self.act_save_file.triggered.connect(self.editor_manager.save_current)

        self.act_save_as = QAction("Save &As...", self)
        self.act_save_as.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.act_save_as.setStatusTip("Save the active document with a new name")
        self.act_save_as.triggered.connect(self.editor_manager.save_current_as)

        self.act_save_all = QAction("Save A&ll", self)
        self.act_save_all.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.act_save_all.setStatusTip("Save all open modified documents")
        self.act_save_all.triggered.connect(self.editor_manager.save_all)

        self.act_close_file = QAction("&Close File", self)
        self.act_close_file.setShortcut(QKeySequence.StandardKey.Close)
        self.act_close_file.setStatusTip("Close the active tab")
        self.act_close_file.triggered.connect(self.editor_manager.close_current_tab)

        self.act_exit = QAction("E&xit", self)
        self.act_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.act_exit.setStatusTip("Exit SmartIDE")
        self.act_exit.triggered.connect(self.close)

        # Edit Actions
        self.act_undo = QAction("&Undo", self)
        self.act_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.act_undo.triggered.connect(self._on_action_undo)

        self.act_redo = QAction("&Redo", self)
        self.act_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.act_redo.triggered.connect(self._on_action_redo)

        self.act_cut = QAction("Cu&t", self)
        self.act_cut.setShortcut(QKeySequence.StandardKey.Cut)
        self.act_cut.triggered.connect(self._on_action_cut)

        self.act_copy = QAction("&Copy", self)
        self.act_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.act_copy.triggered.connect(self._on_action_copy)

        self.act_paste = QAction("&Paste", self)
        self.act_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.act_paste.triggered.connect(self._on_action_paste)

        self.act_select_all = QAction("Select &All", self)
        self.act_select_all.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.act_select_all.triggered.connect(self._on_action_select_all)

        self.act_find_replace = QAction("&Find and Replace...", self)
        self.act_find_replace.setShortcut(QKeySequence.StandardKey.Find)
        self.act_find_replace.triggered.connect(self._on_action_find_replace)

        # View Actions
        self.act_toggle_explorer = self.explorer_dock.toggleViewAction()
        self.act_toggle_explorer.setText("Show Project &Explorer")

        self.act_toggle_db = self.db_dock.toggleViewAction()
        self.act_toggle_db.setText("Show &Database Explorer")

        self.act_toggle_output = self.bottom_dock.toggleViewAction()
        self.act_toggle_output.setText("Show &Output Dock")

        # Run Actions
        self.act_run = QAction("&Run Current File", self)
        self.act_run.setShortcut(QKeySequence("F5"))
        self.act_run.setStatusTip("Execute the current file with Python")
        self.act_run.triggered.connect(self.run_current_file)

        # Database Actions
        self.act_db_connect = QAction("&Connect Database...", self)
        self.act_db_connect.triggered.connect(self._on_action_connect_db)

        self.act_db_new = QAction("&Create New SQLite DB...", self)
        self.act_db_new.triggered.connect(self._on_action_new_db)

        self.act_db_disconnect = QAction("&Disconnect Database", self)
        self.act_db_disconnect.triggered.connect(self._on_action_disconnect_db)

        # Help Actions
        self.act_about = QAction("&About SmartIDE", self)
        self.act_about.triggered.connect(self._on_action_about)

    # -------------------------------------------------------------------------
    # Menus
    # -------------------------------------------------------------------------
    def _create_menus(self) -> None:
        mb = self.menuBar()

        # File Menu
        menu_file = mb.addMenu("&File")
        menu_file.addAction(self.act_new_file)
        menu_file.addAction(self.act_open_file)
        menu_file.addAction(self.act_open_folder)
        menu_file.addSeparator()
        menu_file.addAction(self.act_save_file)
        menu_file.addAction(self.act_save_as)
        menu_file.addAction(self.act_save_all)
        menu_file.addSeparator()
        menu_file.addAction(self.act_close_file)
        menu_file.addSeparator()
        menu_file.addAction(self.act_exit)

        # Edit Menu
        menu_edit = mb.addMenu("&Edit")
        menu_edit.addAction(self.act_undo)
        menu_edit.addAction(self.act_redo)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_cut)
        menu_edit.addAction(self.act_copy)
        menu_edit.addAction(self.act_paste)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_select_all)
        menu_edit.addSeparator()
        menu_edit.addAction(self.act_find_replace)

        # View Menu
        menu_view = mb.addMenu("&View")
        menu_view.addAction(self.act_toggle_explorer)
        menu_view.addAction(self.act_toggle_db)
        menu_view.addAction(self.act_toggle_output)

        # Run Menu
        menu_run = mb.addMenu("&Run")
        menu_run.addAction(self.act_run)

        # Database Menu
        menu_db = mb.addMenu("&Database")
        menu_db.addAction(self.act_db_connect)
        menu_db.addAction(self.act_db_new)
        menu_db.addAction(self.act_db_disconnect)

        # Help Menu
        menu_help = mb.addMenu("&Help")
        menu_help.addAction(self.act_about)

    # -------------------------------------------------------------------------
    # Toolbars
    # -------------------------------------------------------------------------
    def _create_toolbars(self) -> None:
        tb = self.addToolBar("Main Toolbar")
        tb.setObjectName("MainToolBar")
        tb.setMovable(False)

        tb.addAction(self.act_new_file)
        tb.addAction(self.act_open_file)
        tb.addAction(self.act_open_folder)
        tb.addAction(self.act_save_file)
        tb.addAction(self.act_save_all)
        tb.addSeparator()
        tb.addAction(self.act_undo)
        tb.addAction(self.act_redo)
        tb.addAction(self.act_find_replace)
        tb.addSeparator()
        tb.addAction(self.act_run)
        tb.addSeparator()
        tb.addAction(self.act_db_connect)

    # -------------------------------------------------------------------------
    # Status Bar
    # -------------------------------------------------------------------------
    def _create_status_bar(self) -> None:
        sb = QStatusBar(self)
        self.setStatusBar(sb)

        self.lbl_cursor_pos = QLabel("Line 1, Col 1")
        self.lbl_file_info = QLabel("UTF-8")
        self.lbl_lang = QLabel("Plain Text")
        self.lbl_db_status = QLabel("DB: Disconnected")

        sb.addPermanentWidget(self.lbl_db_status)
        sb.addPermanentWidget(self.lbl_cursor_pos)
        sb.addPermanentWidget(self.lbl_lang)
        sb.addPermanentWidget(self.lbl_file_info)

        sb.showMessage("Ready", 3000)

    # -------------------------------------------------------------------------
    # Signal Connections
    # -------------------------------------------------------------------------
    def _connect_signals(self) -> None:
        # File explorer double-click -> open file
        self.file_explorer.file_opened.connect(self._on_file_opened_from_explorer)

        # EditorManager tab changes -> update status bar
        self.editor_manager.tab_changed.connect(self._on_tab_changed)

        # Bottom output controls
        self.btn_clear_output.clicked.connect(self.txt_output.clear)
        self.btn_stop_process.clicked.connect(self._stop_running_process)

        # DB Explorer view table signal
        self.db_explorer.table_selected.connect(self._on_view_table)

    # -------------------------------------------------------------------------
    # State Persistence
    # -------------------------------------------------------------------------
    def _restore_state(self, initial_path: Optional[str] = None) -> None:
        # Restore window geometry
        geom = self.settings.get("window_geometry")
        if geom:
            try:
                self.restoreGeometry(QByteArray.fromHex(geom.encode()))
            except Exception:
                pass

        # Open target file or folder
        if initial_path and os.path.exists(initial_path):
            if os.path.isfile(initial_path):
                self.editor_manager.open_file(Path(initial_path))
                self.file_explorer.set_root_path(str(Path(initial_path).parent))
            else:
                self.file_explorer.set_root_path(initial_path)
                self.settings.set("last_project", initial_path)
        else:
            # Check last project, but make sure it is safe and exists
            last_proj = self.settings.get("last_project")
            if last_proj and os.path.exists(last_proj):
                self.file_explorer.set_root_path(last_proj)

        # Ensure an active editor tab is immediately available to write code
        if self.editor_manager.count() == 0:
            self.editor_manager.new_file()

    def closeEvent(self, event) -> None:
        """Handle window close event with dirty file verification."""
        if not self.editor_manager.close_all_tabs():
            event.ignore()
            return

        # Save geometry
        geom_hex = self.saveGeometry().toHex().data().decode()
        self.settings.set("window_geometry", geom_hex)

        # Kill any running process
        self._stop_running_process()

        # Disconnect DB
        self.db_manager.disconnect()

        event.accept()

    # -------------------------------------------------------------------------
    # Handlers & Slots
    # -------------------------------------------------------------------------
    @Slot(str)
    def _on_file_opened_from_explorer(self, file_path: str) -> None:
        self.editor_manager.open_file(file_path)

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        editor = self.editor_manager.current_editor()
        if editor:
            self.lbl_lang.setText(editor.language.capitalize())
            line = editor.get_current_line()
            col = editor.get_current_column()
            self.lbl_cursor_pos.setText(f"Line {line}, Col {col}")
            editor.cursor_position_changed.connect(self._on_cursor_moved)
        else:
            self.lbl_lang.setText("None")
            self.lbl_cursor_pos.setText("")

    @Slot(int, int)
    def _on_cursor_moved(self, line: int, col: int) -> None:
        self.lbl_cursor_pos.setText(f"Line {line}, Col {col}")

    def _on_action_new_file(self) -> None:
        self.editor_manager.new_file()

    def _on_action_open_file(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Open File",
            "",
            "Python Files (*.py *.pyw);;SQL Files (*.sql);;Text Files (*.txt *.md);;All Files (*.*)"
        )
        for f in files:
            self.editor_manager.open_file(f)

    def _on_action_open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Open Folder / Project")
        if folder:
            self.file_explorer.set_root_path(folder)
            self.settings.set("last_project", folder)
            self.statusBar().showMessage(f"Opened project: {folder}", 3000)

    def _on_action_undo(self) -> None:
        ed = self.editor_manager.current_editor()
        if ed:
            ed.undo()

    def _on_action_redo(self) -> None:
        ed = self.editor_manager.current_editor()
        if ed:
            ed.redo()

    def _on_action_cut(self) -> None:
        ed = self.editor_manager.current_editor()
        if ed:
            ed.cut()

    def _on_action_copy(self) -> None:
        ed = self.editor_manager.current_editor()
        if ed:
            ed.copy()

    def _on_action_paste(self) -> None:
        ed = self.editor_manager.current_editor()
        if ed:
            ed.paste()

    def _on_action_select_all(self) -> None:
        ed = self.editor_manager.current_editor()
        if ed:
            ed.select_all()

    def _on_action_find_replace(self) -> None:
        if self._find_replace_dialog is None:
            self._find_replace_dialog = FindReplaceDialog(self.editor_manager, self)
        self._find_replace_dialog.show()
        self._find_replace_dialog.raise_()
        self._find_replace_dialog.activateWindow()

    # -------------------------------------------------------------------------
    # Code Execution
    # -------------------------------------------------------------------------
    def run_current_file(self) -> None:
        editor = self.editor_manager.current_editor()
        if not editor:
            QMessageBox.information(self, "Run", "No file is open to run.")
            return

        if editor.is_modified() or not editor.file_path:
            # Prompt to save
            saved = self.editor_manager.save_current()
            if not saved:
                return

        file_path = editor.file_path
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "Run Error", "Cannot execute an unsaved file.")
            return

        self._stop_running_process()

        self.txt_output.clear()
        self.txt_output.append(f"=== Running: {file_path} ===\n")
        self.bottom_dock.show()
        self.bottom_dock.raise_()
        self.bottom_tabs.setCurrentWidget(self.output_widget)

        self.process = QProcess(self)
        self.process.setProgram(sys.executable)
        self.process.setArguments(["-u", file_path])
        self.process.setWorkingDirectory(str(Path(file_path).parent))

        self.process.readyReadStandardOutput.connect(self._on_process_stdout)
        self.process.readyReadStandardError.connect(self._on_process_stderr)
        self.process.finished.connect(self._on_process_finished)

        self.btn_stop_process.setEnabled(True)
        self.lbl_process_status.setText("Running...")
        self.process.start()

    def _on_process_stdout(self) -> None:
        if self.process:
            data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
            self.txt_output.insertPlainText(data)

    def _on_process_stderr(self) -> None:
        if self.process:
            data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
            self.txt_output.insertPlainText(data)

    def _on_process_finished(self, exit_code: int) -> None:
        self.txt_output.append(f"\n=== Process finished with exit code {exit_code} ===")
        self.btn_stop_process.setEnabled(False)
        self.lbl_process_status.setText(f"Exited ({exit_code})")
        self.process = None

    def _stop_running_process(self) -> None:
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()
            self.process.waitForFinished(1000)
            self.lbl_process_status.setText("Terminated")
            self.btn_stop_process.setEnabled(False)

    # -------------------------------------------------------------------------
    # Database Actions
    # -------------------------------------------------------------------------
    def _on_action_connect_db(self) -> None:
        db_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select SQLite Database",
            "",
            "SQLite Databases (*.db *.sqlite *.sqlite3);;All Files (*.*)"
        )
        if db_file:
            success, msg = self.db_manager.connect(db_file)
            if success:
                self.lbl_db_status.setText(f"DB: {Path(db_file).name}")
                self.db_explorer.refresh()
                self.sql_console.update_connection_status()
                self.statusBar().showMessage(f"Connected to database: {db_file}", 3000)
            else:
                QMessageBox.critical(self, "Connection Error", f"Failed to connect:\n{msg}")

    def _on_action_new_db(self) -> None:
        db_file, _ = QFileDialog.getSaveFileName(
            self,
            "Create New SQLite Database",
            "",
            "SQLite Databases (*.db *.sqlite3)"
        )
        if db_file:
            # Ensure .db extension
            if not db_file.endswith((".db", ".sqlite", ".sqlite3")):
                db_file += ".db"
            success, msg = self.db_manager.connect(db_file)
            if success:
                self.lbl_db_status.setText(f"DB: {Path(db_file).name}")
                self.db_explorer.refresh()
                self.sql_console.update_connection_status()
                self.statusBar().showMessage(f"Created database: {db_file}", 3000)
            else:
                QMessageBox.critical(self, "Creation Error", f"Failed to create database:\n{msg}")

    def _on_action_disconnect_db(self) -> None:
        self.db_manager.disconnect()
        self.lbl_db_status.setText("DB: Disconnected")
        self.db_explorer.refresh()
        self.sql_console.update_connection_status()
        self.statusBar().showMessage("Database disconnected", 3000)

    @Slot(str)
    def _on_view_table(self, table_name: str) -> None:
        if not self.db_manager.is_connected():
            return
        dialog = TableViewerDialog(self.db_manager, table_name, self)
        dialog.exec()

    def _on_action_about(self) -> None:
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<h3>{APP_NAME} v{APP_VERSION}</h3>"
            f"<p>A professional Python Desktop IDE built with PySide6, QScintilla, and SQLite.</p>"
            f"<p>Features file explorer, syntax highlighting, integrated code runner, and embedded database manager.</p>"
        )
