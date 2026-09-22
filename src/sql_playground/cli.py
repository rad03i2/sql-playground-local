from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .core import Playground, PlaygroundError, QueryResult


def _params(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise PlaygroundError(f"invalid parameter {item!r}; expected name=value")
        name, value = item.split("=", 1)
        if not name:
            raise PlaygroundError("parameter name must not be empty")
        parsed[name] = value
    return parsed


def _cell(value: Any) -> str:
    return "NULL" if value is None else str(value)


def _table(result: QueryResult) -> str:
    if not result.columns:
        return "0 row(s)"
    values = [[_cell(v) for v in row] for row in result.rows]
    widths = [len(name) for name in result.columns]
    for row in values:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))
    header = " | ".join(name.ljust(widths[i]) for i, name in enumerate(result.columns))
    rule = "-+-".join("-" * width for width in widths)
    lines = [header, rule]
    lines.extend(" | ".join(value.ljust(widths[i]) for i, value in enumerate(row)) for row in values)
    lines.append(f"{len(values)} row(s)")
    return "\n".join(lines)


def _print_result(result: QueryResult, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(result.as_dicts(), ensure_ascii=False, indent=2, default=str))
    else:
        print(_table(result))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="sql-playground", description="Local-first SQLite playground")
    p.add_argument("--version", action="version", version=f"sql-playground {__version__} — Radwan Abdulhadi Ahmed / @rad03i2")
    p.add_argument("database", help="SQLite database path")
    sub = p.add_subparsers(dest="command", required=True)

    ex = sub.add_parser("exec", help="execute a trusted SQL script")
    ex.add_argument("source", help=".sql file path, or - for stdin")

    query = sub.add_parser("query", help="run one read-only query")
    query.add_argument("sql")
    query.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    query.add_argument("--format", choices=("table", "json"), default="table")

    schema = sub.add_parser("schema", help="list schema objects")
    schema.add_argument("--format", choices=("table", "json"), default="table")

    desc = sub.add_parser("describe", help="describe a table or view")
    desc.add_argument("name")
    desc.add_argument("--format", choices=("table", "json"), default="table")

    export = sub.add_parser("export", help="export a read-only query to CSV")
    export.add_argument("sql")
    export.add_argument("destination")
    export.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        with Playground(args.database) as db:
            if args.command == "exec":
                if args.source == "-":
                    sql = sys.stdin.read()
                else:
                    sql = Path(args.source).read_text(encoding="utf-8")
                db.execute_script(sql)
                print("Script executed successfully.")
            elif args.command == "query":
                _print_result(db.query(args.sql, _params(args.param)), args.format)
            elif args.command == "schema":
                _print_result(db.schema(), args.format)
            elif args.command == "describe":
                _print_result(db.describe(args.name), args.format)
            elif args.command == "export":
                count = db.export_csv(args.sql, args.destination, _params(args.param))
                print(f"Exported {count} row(s) to {args.destination}")
        return 0
    except (PlaygroundError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
