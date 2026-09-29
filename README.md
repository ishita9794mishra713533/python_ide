# 🚀 SmartIDE - Desktop Python IDE & Database Studio

**SmartIDE** is a modern, lightweight, and feature-rich desktop Integrated Development Environment (IDE) built with **Python 3**, **PySide6 (Qt for Python)**, **QScintilla**, and **SQLite**. 

It is designed for developers, students, and data enthusiasts who need a fast, clean code editor combined with an integrated Python code runner and embedded SQLite database management studio.

---

## 🌟 Key Features

* 📝 **Advanced Code Editor**
  * Built using **QScintilla** (with fallback support).
  * Syntax highlighting for **Python**, **SQL**, **JSON**, **Markdown**, and **Plain Text**.
  * Line numbering, code folding, auto-indentation, and matching bracket guides.
  * Tabbed multi-file interface with dirty file (unsaved changes) indicators.
  * Integrated **Find & Replace** search modal (`Ctrl+F`).

* 📁 **Project & File Explorer**
  * Sidebar tree-view displaying your project's folders and files.
  * Direct file operations: create files/folders, rename, delete, and quick double-click to open in editor.
  * Remembers your last opened project directory automatically.

* ▶️ **Integrated Python Execution Engine**
  * One-click script execution (`F5` or Run button).
  * Real-time streaming of `stdout` (standard output) and `stderr` (error logs).
  * Non-blocking background process execution using `QProcess`.
  * One-click **Stop Process** button to kill long-running scripts or infinite loops.

* 🗄️ **Embedded SQLite Database Studio**
  * Connect to existing `.db` / `.sqlite` files or create brand new SQLite databases.
  * Interactive **Database Explorer** listing all tables, columns, data types, primary keys, and foreign keys.
  * Visual **Table Viewer & Record Editor**: View records in a grid, add new rows, edit existing entries, and delete rows without writing manual SQL commands.
  * Dynamic **Table Creator**: Create new tables visually with custom column names, types, primary keys, non-null, and default values.
  * Full **SQL Console**: Run multi-line custom SQL queries (`SELECT`, `INSERT`, `UPDATE`, `CREATE`, etc.) with instant results in a clean data table or status log.

* 🎨 **Polished Dark Theme & UX**
  * Modern, dark-themed UI palette based on modern IDE design principles.
  * Flexible dockable panel layout (Project Explorer, Database Explorer, Execution Terminal, SQL Console).
  * Status bar showing cursor position (Line/Column), encoding, language mode, and database connection status.

---

## 📂 Project Architecture

The project follows a clean, modular structure separating UI components, database handlers, text editing, and utilities:

```text
python_ide/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies (PySide6, PyQt6-QScintilla)
├── README.md                   # Project documentation & user guide
├── app/                        # Main GUI application & settings
│   ├── main_window.py          # Central QMainWindow coordinating docks, menus & toolbars
│   ├── settings.py            # Persistent application settings manager (QSettings / JSON)
│   └── styles.py              # Qt Dark & Light theme stylesheet definitions
├── editor/                     # Code editing module
│   ├── code_editor.py         # Custom QScintilla / QTextEdit editor component
│   ├── editor_manager.py      # QTabWidget manager handling multi-file tabs & save actions
│   └── syntax_highlighter.py  # Language lexer & syntax highlighting logic
├── explorer/                   # File system explorer module
│   ├── file_explorer.py       # Sidebar tree view widget for files & context menus
│   └── file_manager.py        # File system operations helper (create, delete, rename)
├── database/                   # SQLite database studio module
│   ├── sqlite_manager.py      # SQLite connection & schema inspector
│   ├── database_explorer.py   # Tree view displaying database tables and columns
│   ├── table_viewer.py        # Data grid viewer and GUI record editor
│   ├── sql_console.py         # Query editor and SQL output viewer
│   ├── crud_manager.py        # CRUD helper for database records
│   ├── query_executor.py      # Asynchronous / safe query execution engine
│   └── models.py              # Data structures for table metadata
├── dialogs/                    # Interactive modal dialogs
│   ├── find_replace_dialog.py # Find and replace text dialog
│   ├── create_table_dialog.py # GUI dialog for creating new database tables
│   ├── record_dialog.py       # Insert / edit database record dialog
│   ├── new_file_dialog.py     # Prompt for creating a new file
│   ├── new_folder_dialog.py   # Prompt for creating a new folder
│   └── rename_dialog.py       # Prompt for renaming files/folders
└── utils/                      # Helper tools
    ├── constants.py           # App metadata, file extensions & default settings
    ├── helpers.py             # File path and string formatting utilities
    └── logger.py              # Centralized logging configuration
```

---

## ⚙️ How It Works (Working Mechanism)

1. **Initialization (`main.py`)**:
   * The application parses command-line arguments (such as opening a specific file/folder or resetting saved project settings).
   * It initializes the `QApplication`, applies the custom **Dark Theme**, and launches `MainWindow`.

2. **File Editing (`editor/`)**:
   * The central widget (`EditorManager`) manages multiple document tabs.
   * When a file is opened, `CodeEditor` detects its file extension and attaches the corresponding syntax highlighter (Python, SQL, JSON, Markdown, Text).
   * File modification status (`*` in tab title) is tracked automatically to prompt for unsaved changes before closing.

3. **Code Execution Engine (`main_window.py`)**:
   * When you press `F5` or click **Run Current File**, SmartIDE automatically saves the active file.
   * It launches a subprocess using `QProcess` with your current Python executable (`sys.executable -u <filename>`).
   * Output from standard output (`stdout`) and error output (`stderr`) is captured asynchronously and rendered live in the **Execution Output** terminal pane.
   * If a process gets hung, clicking **Stop Process** sends a termination signal to safely stop execution.

4. **Database Studio (`database/`)**:
   * Connecting to a SQLite database opens a persistent connection via `SQLiteManager`.
   * `DatabaseExplorer` queries the database metadata (`sqlite_master` and `PRAGMA table_info`) to populate the table tree.
   * Double-clicking a table launches the `TableViewerDialog` to view, filter, insert, edit, or delete records.
   * The **SQL Console** allows running raw SQL queries and presents tabular results in a `QTableWidget`.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.8** or higher installed on your system.

### Installation

1. **Clone or download** this repository to your computer.
2. **Open your terminal / command prompt** in the project folder:
   ```bash
   cd path/to/python_ide
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running SmartIDE

Launch the application using Python:

```bash
python main.py
```

#### Optional Command-Line Arguments:
* **Open a specific folder or file on startup**:
  ```bash
  python main.py C:/path/to/my_project
  ```
* **Reset saved project state**:
  ```bash
  python main.py --reset-project
  ```

---

## ⌨️ Useful Keyboard Shortcuts

| Action | Shortcut | Description |
| :--- | :--- | :--- |
| **New Scratch File** | `Ctrl + N` | Creates a new unsaved document tab |
| **Open File** | `Ctrl + O` | Opens a file picker dialog |
| **Open Folder** | `Ctrl + K, Ctrl + O` | Opens a project folder in the explorer |
| **Save File** | `Ctrl + S` | Saves the currently active file |
| **Save All** | `Ctrl + Shift + S` | Saves all open files with unsaved changes |
| **Close Tab** | `Ctrl + W` / `Ctrl + F4` | Closes the current editor tab |
| **Run Python Script** | `F5` | Saves and executes the active file |
| **Find & Replace** | `Ctrl + F` | Opens search and replace modal |
| **Undo / Redo** | `Ctrl + Z` / `Ctrl + Y` | Undo or redo code edits |
| **Exit Application** | `Ctrl + Q` | Closes SmartIDE |

---

## ❓ Frequently Asked Questions (FAQ)

### 1. What is SmartIDE?
**SmartIDE** is a desktop application that lets you write, edit, run Python programs, and inspect SQLite databases all inside one lightweight window without needing heavy IDE software.

### 2. Do I need to install Python separately to run my code?
**Yes.** SmartIDE uses the Python interpreter already installed on your system to execute your scripts. Make sure Python is installed and added to your system environment variables.

### 3. How do I run my Python code?
Open any `.py` file in the editor and press **`F5`** or click the **Run Current File** button on the toolbar. The output will appear in the **Execution Output** tab at the bottom of the window.

### 4. What happens if my script has an infinite loop or gets stuck?
Don't worry! SmartIDE runs your code in an isolated background process. If your script is stuck, simply open the **Execution Output** panel at the bottom and click the red **Stop Process** button.

### 5. How do I connect to a SQLite database?
Click **Database -> Connect Database...** in the top menu bar (or click the database icon on the toolbar). Select your `.db`, `.sqlite`, or `.sqlite3` file. You can also create a new blank database using **Database -> Create New SQLite DB...**.

### 6. Can I view and edit database data without writing SQL?
**Yes!** Once connected, expand the **Database Explorer** panel on the left sidebar, right-click any table, and select **View/Edit Table**. A table grid will pop up allowing you to add, edit, or delete records visually.

### 7. How do I create a new database table visually?
Right-click anywhere inside the **Database Explorer** tree view and select **Create Table...**. You can specify column names, data types (INTEGER, TEXT, REAL, etc.), set primary keys, and configure constraints easily.

### 8. Will SmartIDE remember the folder I opened last time?
**Yes.** SmartIDE automatically remembers your last opened project directory and window size. When you re-open SmartIDE, your project files will be right where you left them.

### 9. Where are application logs saved?
Log files are automatically stored in your user profile folder at:
* **Windows**: `C:\Users\<YourUsername>\.smartide\smartide.log`
* **Linux/macOS**: `~/.smartide/smartide.log`

### 10. Can I customize or switch themes?
SmartIDE defaults to a dark theme. Additional theme definitions and stylesheet configurations can be found inside [`app/styles.py`](file:///c:/Users/hp/Desktop/python_ide/app/styles.py).

---

## 📄 License & Attribution

Built with ❤️ using **Python**, **PySide6**, **QScintilla**, and **SQLite**. Free for educational and personal use.
