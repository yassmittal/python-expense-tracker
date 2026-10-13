"""Pydantic models: the *shape* of the data that goes in and out of the API.

In the CLI version, models.py had dataclasses and we validated input by hand
(Expense.parse_amount). In FastAPI, Pydantic does that work for us:

  - FastAPI reads the JSON body of a request.
  - Pydantic checks every field (type, rules like "greater than 0").
  - If something is wrong, FastAPI automatically replies with a 422 error
    explaining which field failed. Our route function never even runs.

A common pattern is to have separate models for:
  - what the client SENDS   (ExpenseCreate - no id, the server makes the id)
  - what the server RETURNS (Expense - includes the id)
"""

import datetime

from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    """The JSON body a client sends to POST /expenses.

    Example body:
        {"title": "Lunch", "category": "food", "amount": 120.5}
    """

    # Field(...) lets us add rules and docs to a field.
    # min_length=1 rejects an empty string "".
    title: str = Field(min_length=1, examples=["Lunch"])
    category: str = Field(min_length=1, examples=["food"])

    # gt=0 means "greater than 0". Sending 0 or -5 gives an automatic 422 error.
    # (Real money apps often use Decimal or whole paise as int; float keeps
    # this learning project simple.)
    amount: float = Field(gt=0, examples=[120.5])

    # default_factory is called each time a default is needed, so every new
    # expense gets *today's* date if the client does not send one.
    # Pydantic also accepts the text "2026-10-13" and turns it into a date object.
    #
    # Why `datetime.date` and not `from datetime import date`? Because the
    # FIELD is also called `date`. Writing `date: date = ...` makes Python
    # confuse the field name with the type, and Pydantic raises an error.
    date: datetime.date = Field(default_factory=datetime.date.today)

    # A validator is your own extra check/cleanup for a field. It runs after
    # Pydantic's built-in checks (like min_length) have passed.
    # This one does what Expense.__post_init__ did in models.py: tidy the text.
    # Lowercasing means "Food" and "food" count as ONE category in /summary.
    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            # A ValueError here becomes a normal 422 error for the client.
            raise ValueError("category cannot be only spaces")
        return value  # Whatever we return is the value that gets stored.


class Expense(ExpenseCreate):
    """An expense as the API returns it.

    It inherits title, category, amount and date from ExpenseCreate
    (same idea as Expense inheriting from Transaction in models.py)
    and only adds the id the server generated.
    """

    id: int


class CategoryTotal(BaseModel):
    """One row of the per-category breakdown in GET /summary."""

    category: str
    total: float
    count: int


class Summary(BaseModel):
    """The response of GET /summary.

    Models can contain other models and lists of models; FastAPI turns the
    whole thing into nested JSON and shows the structure in /docs.
    """

    total_spent: float
    expense_count: int
    by_category: list[CategoryTotal]

    # "Expense | None" means: an Expense object OR null (when there are no expenses).
    highest: Expense | None
    lowest: Expense | None
    top_three: list[Expense]
