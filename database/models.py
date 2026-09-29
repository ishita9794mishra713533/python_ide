"""Data models and structures for database operations."""
from dataclasses import dataclass, field
from typing import List, Any, Optional, Dict


@dataclass
class ColumnInfo:
    """Represents column metadata."""
    cid: int
    name: str
    data_type: str
    not_null: bool = False
    default_value: Any = None
    is_primary_key: bool = False


@dataclass
class TableSchema:
    """Represents a SQLite table schema with columns."""
    name: str
    columns: List[ColumnInfo] = field(default_factory=list)
    sql: str = ""

    def get_primary_keys(self) -> List[str]:
        """Return list of column names that form the primary key."""
        return [c.name for c in self.columns if c.is_primary_key]


# Alias for compatibility
TableInfo = TableSchema


@dataclass
class QueryResult:
    """Represents result of a SQL query execution."""
    success: bool
    columns: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)
    rows_affected: int = 0
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None
