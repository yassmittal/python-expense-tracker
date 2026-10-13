"""Storage version 1: keep expenses in a plain Python list (in memory).

Simple and great for learning, but everything disappears when the server
restarts (and `uvicorn --reload` restarts it every time you save a file!).
sqlite_storage.py has the exact same functions but saves to a database file.

Because both files have the same function names, main.py can switch between
them by changing a single import line.
"""

from schemas import Expense, ExpenseCreate


# Module-level variables live as long as the server process is running.
expenses: list[Expense] = []
next_id = 1  # The id we will give to the next new expense.


def setup() -> None:
    """Nothing to prepare for a list. (sqlite_storage creates a table here.)"""


def get_all(category: str | None = None) -> list[Expense]:
    """Return every expense, or only those in one category if given."""
    if category is None:
        return expenses

    # .lower() on both sides makes the filter case-insensitive:
    # ?category=FOOD finds expenses saved as "food" or "Food".
    return [e for e in expenses if e.category.lower() == category.lower()]


def get_one(expense_id: int) -> Expense | None:
    """Return the expense with this id, or None if it does not exist."""
    for expense in expenses:
        if expense.id == expense_id:
            return expense
    return None


def add(new_expense: ExpenseCreate) -> Expense:
    """Give the new expense an id, store it, and return the stored version."""
    # `global` lets this function change the module-level next_id variable.
    # Without it, `next_id += 1` would raise an UnboundLocalError.
    global next_id

    # model_dump() turns a Pydantic model into a plain dict:
    #   {"title": "Lunch", "category": "food", "amount": 120.5, "date": ...}
    # **dict unpacks it into keyword arguments: Expense(id=1, title="Lunch", ...)
    expense = Expense(id=next_id, **new_expense.model_dump())
    expenses.append(expense)
    next_id += 1
    return expense


def delete(expense_id: int) -> bool:
    """Remove the expense. Return True if it existed, False if not."""
    expense = get_one(expense_id)
    if expense is None:
        return False
    expenses.remove(expense)
    return True
