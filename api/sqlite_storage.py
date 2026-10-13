"""Storage version 2 (stretch goal): save expenses in a SQLite database.

SQLite is a whole SQL database stored in ONE file (expenses.db). It is built
into Python (`import sqlite3`), so there is nothing to install.

This file has the same functions as list_storage.py, so main.py does not
care which one it uses. Only the "how do we store it" part changes.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from schemas import Expense, ExpenseCreate


# Same trick as storage.py in the CLI: put the file next to this .py file,
# no matter which folder you start uvicorn from.
DB_FILE = Path(__file__).with_name("expenses.db")


@contextmanager
def get_connection():
    """Open the database, hand it to a `with` block, then save and close it.

    @contextmanager turns this generator into something usable with `with`:

        with get_connection() as connection:
            ...  # code here runs at the `yield`

    Why a new connection for each request? FastAPI runs normal `def` routes
    in several threads, and a sqlite3 connection should not be shared
    between threads. Opening one per call is simple and safe.
    """
    connection = sqlite3.connect(DB_FILE)
    # Row lets us read columns by name: row["title"] instead of row[1].
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()  # Save changes (only reached if no error happened).
    finally:
        connection.close()  # Always runs, even if there was an error.


def row_to_expense(row: sqlite3.Row) -> Expense:
    """Turn a database row into a Pydantic Expense.

    dict(row) -> {"id": 1, "title": "Lunch", ..., "date": "2026-10-13"}
    Pydantic converts the "2026-10-13" text back into a date object.
    """
    return Expense(**dict(row))


def setup() -> None:
    """Create the table once. IF NOT EXISTS makes it safe to run every start."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                title    TEXT NOT NULL,
                category TEXT NOT NULL,
                amount   REAL NOT NULL,
                date     TEXT NOT NULL
            )
            """
        )
        # INTEGER PRIMARY KEY AUTOINCREMENT: SQLite creates the id for us,
        # so we do not need the next_id counter from list_storage.py.


def get_all(category: str | None = None) -> list[Expense]:
    """Return every expense, or only those in one category if given."""
    with get_connection() as connection:
        if category is None:
            rows = connection.execute("SELECT * FROM expenses ORDER BY id").fetchall()
        else:
            # NEVER build SQL with f-strings from user input (SQL injection!).
            # Use ? placeholders and pass the values separately as a tuple.
            # Note the trailing comma: (category,) is a tuple with one item.
            rows = connection.execute(
                "SELECT * FROM expenses WHERE LOWER(category) = LOWER(?) ORDER BY id",
                (category,),
            ).fetchall()
    return [row_to_expense(row) for row in rows]


def get_one(expense_id: int) -> Expense | None:
    """Return the expense with this id, or None if it does not exist."""
    with get_connection() as connection:
        # fetchone() returns one row, or None when nothing matched.
        row = connection.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
    return row_to_expense(row) if row else None


def add(new_expense: ExpenseCreate) -> Expense:
    """Insert the expense and return it with the id SQLite generated."""
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO expenses (title, category, amount, date) VALUES (?, ?, ?, ?)",
            (
                new_expense.title,
                new_expense.category,
                new_expense.amount,
                new_expense.date.isoformat(),  # date object -> "2026-10-13" text
            ),
        )
        # lastrowid is the id SQLite just gave to the inserted row.
        new_id = cursor.lastrowid
    return Expense(id=new_id, **new_expense.model_dump())


def delete(expense_id: int) -> bool:
    """Delete the expense. Return True if a row was deleted, False if not."""
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    # rowcount = how many rows the DELETE removed (0 means the id was not there).
    return cursor.rowcount > 0
