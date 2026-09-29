"""SQLite Database connection and metadata manager."""
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

from utils.logger import get_logger
from database.models import ColumnInfo, TableSchema
from database.query_executor import QueryExecutor

logger = get_logger("sqlite_manager")


class SQLiteManager:
    """Manages SQLite connection lifecycle, database creation, and metadata introspection."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path: Optional[Path] = None
        self.connection: Optional[sqlite3.Connection] = None
        self.executor = QueryExecutor()

        if db_path:
            self.connect(db_path)

    def is_connected(self) -> bool:
        if not self.connection:
            return False
        try:
            self.connection.execute("SELECT 1")
            return True
        except Exception:
            return False

    def connect(self, db_path: Path | str, create_if_missing: bool = True) -> Tuple[bool, str]:
        self.disconnect()

        p = Path(db_path).resolve()
        if not p.exists() and not create_if_missing:
            return False, f"Database file does not exist:\n{p}"

        if not p.parent.exists():
            return False, f"Directory does not exist:\n{p.parent}"

        try:
            conn = sqlite3.connect(str(p), check_same_thread=False)
            conn.row_factory = None
            cursor = conn.cursor()
            cursor.execute("PRAGMA quick_check")
            cursor.fetchone()
            cursor.close()

            self.connection = conn
            self.db_path = p
            self.executor.set_connection(conn)
            logger.info("Connected to SQLite database: %s", p)
            return True, f"Connected to {p.name}"
        except sqlite3.DatabaseError as e:
            msg = f"Invalid SQLite database: {e}"
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Failed to connect to database: {e}"
            logger.error(msg)
            return False, msg

    def create_database(self, db_path: Path | str) -> Tuple[bool, str]:
        p = Path(db_path).resolve()
        if p.exists():
            return False, f"File already exists:\n{p}"

        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(p), check_same_thread=False)
            conn.execute("VACUUM")
            conn.commit()
            conn.close()

            logger.info("Created new SQLite database: %s", p)
            return self.connect(p)
        except Exception as e:
            msg = f"Failed to create database: {e}"
            logger.error(msg)
            return False, msg

    def disconnect(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logger.warning("Error closing SQLite connection: %s", e)
            finally:
                self.connection = None
                self.db_path = None
                self.executor.set_connection(None)
                logger.info("SQLite database disconnected.")

    def get_tables(self) -> List[str]:
        if not self.is_connected():
            return []

        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        result = self.executor.execute_query(sql)
        if result.success:
            return [row[0] for row in result.rows]
        return []

    def get_views(self) -> List[str]:
        if not self.is_connected():
            return []

        sql = "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;"
        result = self.executor.execute_query(sql)
        if result.success:
            return [row[0] for row in result.rows]
        return []

    def get_table_schema(self, table_name: str) -> Optional[TableSchema]:
        if not self.is_connected():
            return None

        sql_ddl = "SELECT sql FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?;"
        ddl_res = self.executor.execute_query(sql_ddl, (table_name,))
        ddl_text = ddl_res.rows[0][0] if ddl_res.success and ddl_res.rows else ""

        pragma_sql = f'PRAGMA table_info("{table_name}");'
        res = self.executor.execute_query(pragma_sql)
        if not res.success:
            return None

        columns = []
        for row in res.rows:
            cid = int(row[0])
            name = str(row[1])
            data_type = str(row[2]) if row[2] else "TEXT"
            not_null = bool(row[3])
            default_val = row[4]
            is_pk = bool(row[5])

            col = ColumnInfo(
                cid=cid,
                name=name,
                data_type=data_type,
                not_null=not_null,
                default_value=default_val,
                is_primary_key=is_pk,
            )
            columns.append(col)

        return TableSchema(name=table_name, columns=columns, sql=ddl_text)

    def get_row_count(self, table_name: str) -> int:
        if not self.is_connected():
            return 0
        sql = f'SELECT COUNT(*) FROM "{table_name}";'
        res = self.executor.execute_query(sql)
        if res.success and res.rows:
            return int(res.rows[0][0])
        return 0

    def execute_script(self, sql_script: str) -> Tuple[bool, Optional[str]]:
        """Execute a multi-statement SQL script."""
        if not self.is_connected() or not self.connection:
            return False, "Not connected to any database."
        try:
            self.connection.executescript(sql_script)
            self.connection.commit()
            return True, None
        except Exception as e:
            logger.error("Error executing SQL script: %s", e)
            return False, str(e)

    def get_table_names(self) -> List[str]:
        """Alias for get_tables."""
        return self.get_tables()

    def get_columns(self, table_name: str) -> List[ColumnInfo]:
        """Return columns for a given table."""
        schema = self.get_table_schema(table_name)
        return schema.columns if schema else []
