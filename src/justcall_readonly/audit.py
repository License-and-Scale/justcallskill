"""SQLite audit log for every tool invocation.

Every call the agent makes — even read-only ones — is logged with
timestamp, tool name, arguments, and outcome. This gives operators a
trail to review if the agent behaves unexpectedly.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Any

DB_PATH = os.environ.get("JUSTCALL_AUDIT_DB", os.path.expanduser("~/.justcall-audit.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    tool TEXT NOT NULL,
    args TEXT NOT NULL,
    outcome TEXT NOT NULL,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_invocations_ts ON invocations(ts);
CREATE INDEX IF NOT EXISTS idx_invocations_tool ON invocations(tool);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    return conn


@contextmanager
def record(tool: str, args: dict[str, Any]):
    start = time.time()
    error: str | None = None
    outcome = "ok"
    try:
        yield
    except Exception as e:
        outcome = "error"
        error = f"{type(e).__name__}: {e}"
        raise
    finally:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO invocations (ts, tool, args, outcome, error) VALUES (?, ?, ?, ?, ?)",
                (start, tool, json.dumps(args, default=str), outcome, error),
            )
