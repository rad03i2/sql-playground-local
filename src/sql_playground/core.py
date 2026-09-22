from __future__ import annotations

import csv
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

_READ_ONLY = re.compile(r"^\s*(?:--[^\n]*\n\s*)*(SELECT|WITH|PRAGMA|EXPLAIN)\b", re.IGNORECASE)


class PlaygroundError(Exception):
    """User-facing playground error."""


@dataclass(frozen=True)
class QueryResult:
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]

    def as_dicts(self) -> list[dict[str, Any]]:
        return [dict(zip(self.columns, row)) for row in self.rows]


class Playground:
    def __init__(self, database: str | Path, *, timeout: float = 5.0) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.database = str(database)
        self.connection = sqlite3.connect(self.database, timeout=timeout)
        self.connection.execute("PRAGMA foreign_keys = ON")

    def __enter__(self) -> "Playground":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _ensure_read_only(sql: str) -> None:
        if not sql.strip():
            raise PlaygroundError("query must not be empty")
        if not _READ_ONLY.match(sql):
            raise PlaygroundError("query/export accepts read-only SELECT, WITH, PRAGMA, or EXPLAIN SQL only")
        # sqlite3.execute itself rejects multiple statements. Keep semicolons inside literals valid.

    def query(self, sql: str, params: Mapping[str, Any] | Sequence[Any] | None = None) -> QueryResult:
        self._ensure_read_only(sql)
        try:
            cursor = self.connection.execute(sql, params or {})
            if cursor.description is None:
                raise PlaygroundError("statement did not produce a result set")
            columns = tuple(item[0] for item in cursor.description)
            rows = tuple(tuple(row) for row in cursor.fetchall())
            return QueryResult(columns, rows)
        except sqlite3.Error as exc:
            raise PlaygroundError(str(exc)) from exc

    def execute_script(self, sql: str) -> None:
        if not sql.strip():
            raise PlaygroundError("SQL script is empty")
        try:
            self.connection.executescript("BEGIN;\n" + sql + "\nCOMMIT;")
        except sqlite3.Error as exc:
            try:
                self.connection.rollback()
            except sqlite3.Error:
                pass
            raise PlaygroundError(str(exc)) from exc

    def schema(self) -> QueryResult:
        return self.query(
            "SELECT type, name, tbl_name FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )

    def describe(self, name: str) -> QueryResult:
        if not name or "\x00" in name:
            raise PlaygroundError("invalid object name")
        # PRAGMA does not support bound identifiers; quote an already validated string safely.
        quoted = name.replace('"', '""')
        result = self.query(f'PRAGMA table_info("{quoted}")')
        if not result.rows:
            raise PlaygroundError(f"table or view not found: {name}")
        return result

    def export_csv(self, sql: str, destination: str | Path, params: Mapping[str, Any] | None = None) -> int:
        result = self.query(sql, params)
        path = Path(destination)
        if path.exists() and path.is_dir():
            raise PlaygroundError(f"destination is a directory: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(result.columns)
                writer.writerows(result.rows)
        except OSError as exc:
            raise PlaygroundError(str(exc)) from exc
        return len(result.rows)
