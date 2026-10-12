"""Reading and writing expense data to a JSON file."""

import json
from pathlib import Path

from models import Expense


DATA_FILE = Path(__file__).with_name("expenses.json")


def load_expenses() -> list[Expense]:
    """Load JSON text, turn it into Python data, then into Expense objects."""
    if not DATA_FILE.exists():
        return []

    try:
        # `with` always closes the file, even if reading fails.
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.loads(file.read())  # JSON text -> Python list of dictionaries
        return [Expense.from_dict(item) for item in data]
    except (json.JSONDecodeError, OSError, KeyError, ValueError):
        print("Could not read expenses.json. Starting with an empty list.")
        return []


def save_expenses(expenses: list[Expense]) -> None:
    """Turn Expense objects into JSON text and save it."""
    data = [expense.to_dict() for expense in expenses]
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write(json.dumps(data, indent=2))  # Python data -> JSON text
