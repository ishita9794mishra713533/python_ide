"""CRUD Operations Manager for SQLite with parameterized queries."""
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import get_logger
from database.models import QueryResult, ColumnInfo
from database.sqlite_manager import SQLiteManager

logger = get_logger("crud_manager")


class CRUDManager:
    """Provides high-level, parameterized CRUD operations for SQLite tables."""

    def __init__(self, sqlite_manager: SQLiteManager):
        self.sqlite_manager = sqlite_manager

    @property
    def executor(self):
        return self.sqlite_manager.executor

    def create_table(self, table_name: str, columns: List[Dict[str, Any]]) -> QueryResult:
        clean_name = table_name.strip()
        if not clean_name:
            return QueryResult(success=False, error_message="Table name cannot be empty.")
        if not columns:
            return QueryResult(success=False, error_message="Table must have at least one column.")

        col_defs = []
        for col in columns:
            name = col["name"].strip()
            dtype = col.get("type", "TEXT").upper()
            parts = [f'"{name}" {dtype}']
            if col.get("primary_key", False):
                parts.append("PRIMARY KEY")
            if col.get("not_null", False):
                parts.append("NOT NULL")
            col_defs.append(" ".join(parts))

        sql = f'CREATE TABLE "{clean_name}" (\n    ' + ",\n    ".join(col_defs) + "\n);"
        logger.info("Executing create table SQL:\n%s", sql)
        return self.executor.execute_query(sql)

    def drop_table(self, table_name: str) -> QueryResult:
        sql = f'DROP TABLE IF EXISTS "{table_name}";'
        return self.executor.execute_query(sql)

    def select_data(
        self,
        table_name: str,
        limit: int = 500,
        offset: int = 0,
        search_filter: Optional[str] = None,
    ) -> QueryResult:
        schema = self.sqlite_manager.get_table_schema(table_name)
        if not schema:
            return QueryResult(success=False, error_message=f"Table '{table_name}' does not exist.")

        sql = f'SELECT * FROM "{table_name}"'
        params: List[Any] = []

        if search_filter and search_filter.strip():
            clean_search = f"%{search_filter.strip()}%"
            where_clauses = [f'CAST("{col.name}" AS TEXT) LIKE ?' for col in schema.columns]
            if where_clauses:
                sql += " WHERE " + " OR ".join(where_clauses)
                params.extend([clean_search] * len(where_clauses))

        sql += f" LIMIT {int(limit)} OFFSET {int(offset)};"
        return self.executor.execute_query(sql, tuple(params) if params else None)

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> QueryResult:
        if not data:
            return QueryResult(success=False, error_message="No record data provided to insert.")

        columns = list(data.keys())
        values = list(data.values())
        col_names = ", ".join([f'"{c}"' for c in columns])
        placeholders = ", ".join(["?"] * len(columns))

        sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders});'
        return self.executor.execute_query(sql, tuple(values))

    def update_record(
        self,
        table_name: str,
        data: Dict[str, Any],
        key_conditions: Dict[str, Any],
    ) -> QueryResult:
        if not data:
            return QueryResult(success=False, error_message="No update data provided.")
        if not key_conditions:
            return QueryResult(success=False, error_message="No key conditions specified for update.")

        set_clause = ", ".join([f'"{k}" = ?' for k in data.keys()])
        where_clause = " AND ".join([f'"{k}" = ?' for k in key_conditions.keys()])

        params = list(data.values()) + list(key_conditions.values())
        sql = f'UPDATE "{table_name}" SET {set_clause} WHERE {where_clause};'
        return self.executor.execute_query(sql, tuple(params))

    def delete_record(self, table_name: str, key_conditions: Dict[str, Any]) -> QueryResult:
        if not key_conditions:
            return QueryResult(success=False, error_message="No conditions specified for deletion.")

        where_clause = " AND ".join([f'"{k}" = ?' for k in key_conditions.keys()])
        params = list(key_conditions.values())
        sql = f'DELETE FROM "{table_name}" WHERE {where_clause};'
        return self.executor.execute_query(sql, tuple(params))
