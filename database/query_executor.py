"""Safe SQL query executor for SQLite."""
import time
import sqlite3
from typing import Any, List, Optional, Tuple
from utils.logger import get_logger
from database.models import QueryResult

logger = get_logger("query_executor")


class QueryExecutor:
    """Executes arbitrary SQL queries safely on a SQLite connection."""

    def __init__(self, connection: Optional[sqlite3.Connection] = None):
        self.connection = connection

    def set_connection(self, connection: Optional[sqlite3.Connection]) -> None:
        self.connection = connection

    def execute_query(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> QueryResult:
        if not self.connection:
            return QueryResult(
                success=False,
                error_message="No database connection. Please connect to a database first."
            )

        clean_sql = sql.strip()
        if not clean_sql:
            return QueryResult(success=True, error_message="Empty query.")

        start_time = time.perf_counter()
        cursor = None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(clean_sql, params)
            else:
                cursor.execute(clean_sql)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = [list(row) for row in cursor.fetchall()]
                return QueryResult(
                    success=True,
                    columns=columns,
                    rows=rows,
                    rows_affected=len(rows),
                    execution_time_ms=elapsed_ms,
                )
            else:
                self.connection.commit()
                return QueryResult(
                    success=True,
                    rows_affected=cursor.rowcount,
                    execution_time_ms=elapsed_ms,
                )
        except sqlite3.Error as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = str(e)
            logger.warning("SQL Execution Error: %s in query: %s", error_msg, clean_sql[:100])
            return QueryResult(
                success=False,
                execution_time_ms=elapsed_ms,
                error_message=error_msg,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error("Unexpected error in SQL executor: %s", e)
            return QueryResult(
                success=False,
                execution_time_ms=elapsed_ms,
                error_message=f"Unexpected error: {e}",
            )
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
