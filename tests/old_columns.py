import sqlite3

from journal.db.migrations.column_renames import COMMON_COLUMNS, TABLES
from journal.db.migrations.type_columns import RENAMED

LATER_RENAMES = {"agents": {"has_overview": "is_overview_read"}}


def old_columns(db: sqlite3.Connection) -> None:
    """Gives a journal's tables back the column names the migrations before ColumnRenames read and write."""
    for (table,) in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall():
        for old, new in LATER_RENAMES.get(table, {}).items():
            if new in {row[1] for row in db.execute(f"PRAGMA table_info({table})")}:
                db.execute(f"ALTER TABLE {table} RENAME COLUMN {new} TO {old}")
        present = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
        for old, new in {**COMMON_COLUMNS, **TABLES.get(table, {})}.items():
            if new in present and old not in present:
                db.execute(f"ALTER TABLE {table} RENAME COLUMN {new} TO {old}")
    kind_columns(db)


def kind_columns(db: sqlite3.Connection) -> None:
    """Gives a journal's tables back the columns named kind that the migrations before TypeColumns read and write."""
    for model in RENAMED:
        present = {row[1] for row in db.execute(f"PRAGMA table_info({model.storage()})").fetchall()}
        for old, new in model.column_renames.items():
            if new in present and old not in present:
                db.execute(f"ALTER TABLE {model.storage()} RENAME COLUMN {new} TO {old}")
