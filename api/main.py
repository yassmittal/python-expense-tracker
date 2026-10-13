"""The FastAPI version of the expense tracker.

Run it (from inside the api/ folder):
    uvicorn main:app --reload

    main  -> this file (main.py)
    app   -> the `app = FastAPI()` variable below
    --reload -> restart the server automatically when you save a file

Then open http://localhost:8000/docs to try every endpoint in the browser.

The CLI had a menu (1. Add, 2. View, ...). An API has no menu: instead each
action is a URL + an HTTP method:

    CLI menu option      HTTP method + path
    ---------------      ------------------
    2. View expenses     GET    /expenses
    1. Add expense       POST   /expenses
    4. Delete expense    DELETE /expenses/{expense_id}
    3. View summary      GET    /summary
"""

import heapq
from collections import Counter, defaultdict

from fastapi import FastAPI, HTTPException, status

from schemas import CategoryTotal, Expense, ExpenseCreate, Summary

# Pick where the data lives. Both modules have the same functions
# (setup, get_all, get_one, add, delete), so only this line changes:
#   import list_storage as storage     # in memory, lost on restart
#   import sqlite_storage as storage   # saved in expenses.db
import sqlite_storage as storage


# The application object. uvicorn looks for this variable.
# title/description appear at the top of the /docs page.
app = FastAPI(
    title="Expense Tracker API",
    description="The CLI expense tracker, rebuilt as a web API.",
)

# Create the database table (if needed) once, when the server starts.
storage.setup()


# ---------------------------------------------------------------------------
# GET /expenses  (optional ?category=food filter)
# ---------------------------------------------------------------------------
# @app.get("/expenses") is a decorator: it registers the function below so
# that a GET request to /expenses calls it.
#
# response_model tells FastAPI the shape of what we return. FastAPI uses it
# to (1) convert our objects to JSON, (2) filter out extra fields, and
# (3) show the response shape in /docs.
@app.get("/expenses", response_model=list[Expense])
def list_expenses(category: str | None = None):
    # `category` is NOT part of the path ("/expenses"), so FastAPI treats it
    # as a QUERY parameter: /expenses?category=food
    # The default `= None` makes it optional: plain /expenses also works.
    return storage.get_all(category)


# ---------------------------------------------------------------------------
# GET /expenses/{expense_id}  -> 404 if missing
# ---------------------------------------------------------------------------
# {expense_id} in the path is a PATH parameter. Its name must match the
# function argument. The type hint `int` makes FastAPI convert "3" -> 3,
# and /expenses/abc gets an automatic 422 error (not a number).
@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int):
    expense = storage.get_one(expense_id)
    if expense is None:
        # `raise` stops the function immediately. FastAPI catches the
        # HTTPException and sends:  404  {"detail": "Expense 7 not found"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # same as status_code=404
            detail=f"Expense {expense_id} not found",
        )
    return expense


# ---------------------------------------------------------------------------
# POST /expenses  with a Pydantic body (amount must be > 0)
# ---------------------------------------------------------------------------
# status_code=201 means "Created". It is the usual reply when POST makes
# something new (the default for success is 200 "OK").
@app.post("/expenses", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(new_expense: ExpenseCreate):
    # Because the type hint is a Pydantic model (ExpenseCreate), FastAPI
    # reads it from the JSON REQUEST BODY and validates it BEFORE this line.
    # So in here we already know amount > 0 and title is not empty.
    # Compare with ask_for_amount() in the CLI, which needed a while loop!
    return storage.add(new_expense)


# ---------------------------------------------------------------------------
# DELETE /expenses/{expense_id}
# ---------------------------------------------------------------------------
# 204 means "No Content": success, and there is nothing to send back.
@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    was_deleted = storage.delete(expense_id)
    if not was_deleted:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    # Returning None is correct for 204: the response body stays empty.


# ---------------------------------------------------------------------------
# GET /summary
# ---------------------------------------------------------------------------
# Same calculations as show_summary() in expense_tracker.py, but instead of
# print()-ing the results we RETURN them, and FastAPI turns them into JSON.
@app.get("/summary", response_model=Summary)
def get_summary():
    expenses = storage.get_all()

    # Early return for the empty case: max()/min() would crash on an empty list.
    if not expenses:
        return Summary(
            total_spent=0,
            expense_count=0,
            by_category=[],
            highest=None,
            lowest=None,
            top_three=[],
        )

    # defaultdict(float) starts every new category at 0.0 automatically.
    totals: defaultdict[str, float] = defaultdict(float)
    for expense in expenses:
        totals[expense.category] += expense.amount

    # Counter counts how many expenses each category has, in one line.
    counts = Counter(expense.category for expense in expenses)

    # Build one CategoryTotal per category, largest total first.
    by_category = [
        CategoryTotal(category=category, total=round(total, 2), count=counts[category])
        for category, total in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ]

    return Summary(
        # round(..., 2) because floats can give 0.30000000000000004.
        total_spent=round(sum(expense.amount for expense in expenses), 2),
        expense_count=len(expenses),
        by_category=by_category,
        highest=max(expenses, key=lambda expense: expense.amount),
        lowest=min(expenses, key=lambda expense: expense.amount),
        top_three=heapq.nlargest(3, expenses, key=lambda expense: expense.amount),
    )
