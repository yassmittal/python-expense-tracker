"""Automated checks. Run with: python3 -m unittest -v"""

import unittest
from decimal import Decimal
from unittest.mock import patch

from expense_tracker import show_summary
from models import Expense


class ExpenseTrackerTests(unittest.TestCase):
    def test_summary_groups_categories_and_totals(self) -> None:
        expenses = [
            Expense("Lunch", "2026-01-01", "Food", Decimal("100")),
            Expense("Bus", "2026-01-01", "Travel", Decimal("30.50")),
            Expense("Coffee", "2026-01-02", "Food", Decimal("20")),
        ]
        with patch("builtins.print") as mock_print:
            show_summary(expenses)

        output = "\n".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Food", output)
        self.assertIn("₹120.00", output)
        self.assertIn("₹150.50", output)

    def test_dataclass_equality_and_json_conversion(self) -> None:
        expense = Expense("Book", "2026-01-01", "Learning", Decimal("499"))
        self.assertEqual(expense, Expense.from_dict(expense.to_dict()))

    def test_invalid_amount_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Expense.parse_amount("not a number")


if __name__ == "__main__":
    unittest.main()
