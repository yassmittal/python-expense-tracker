"""The data models used by the expense tracker.

Keeping classes here lets other files import them with:
    from models import Expense
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class Transaction:
    """A base class shared by anything that has a title and a date."""

    title: str
    date: str

    def __post_init__(self) -> None:
        # __post_init__ runs after dataclass creates __init__ for us.
        self.title = self.title.strip() or "Untitled expense"


@dataclass
class Expense(Transaction):
    """One expense. It inherits title and date from Transaction."""

    category: str
    amount: Decimal

    def __post_init__(self) -> None:
        super().__post_init__()  # Run Transaction's setup before our own.
        self.category = self.category.strip() or "Other"
        if self.amount <= 0:
            raise ValueError("An expense amount must be greater than zero.")

    def __str__(self) -> str:
        """The friendly version shown when someone calls print(expense)."""
        return f"{self.date} | {self.category}: {self.title} — ₹{self.amount:.2f}"

    def __repr__(self) -> str:
        """The developer-friendly version shown in lists and the REPL."""
        return (
            "Expense("
            f"title={self.title!r}, category={self.category!r}, "
            f"amount={self.amount!r}, date={self.date!r})"
        )

    @staticmethod
    def parse_amount(raw_amount: str) -> Decimal:
        """Turn text into money; no existing Expense object is needed."""
        try:
            amount = Decimal(raw_amount).quantize(Decimal("0.01"))
        except InvalidOperation as error:
            raise ValueError("Enter a number, for example 125 or 49.50.") from error

        if amount <= 0:
            raise ValueError("Enter an amount greater than zero.")
        return amount

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Expense":
        """Build an Expense from JSON data. cls means this also supports subclasses."""
        return cls(
            title=data["title"],
            category=data["category"],
            amount=cls.parse_amount(data["amount"]),
            date=data["date"],
        )

    def to_dict(self) -> dict[str, str]:
        """Return JSON-friendly data (JSON does not understand Decimal)."""
        return {
            "title": self.title,
            "category": self.category,
            "amount": str(self.amount),
            "date": self.date,
        }
