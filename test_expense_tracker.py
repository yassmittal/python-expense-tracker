"""Small automated checks for the expense tracker.

Run with: python3 -m unittest -v
"""

import unittest
from decimal import Decimal
from unittest.mock import patch

import expense_tracker


class ExpenseTrackerTests(unittest.TestCase):
    def test_summary_adds_each_category_and_total(self):
        expenses = [
            {"title": "Lunch", "category": "Food", "amount": "100", "date": "2026-01-01"},
            {"title": "Bus", "category": "Travel", "amount": "30.50", "date": "2026-01-01"},
            {"title": "Coffee", "category": "Food", "amount": "20", "date": "2026-01-02"},
        ]

        with patch("builtins.print") as mock_print:
            expense_tracker.show_summary(expenses)

        output = "\n".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Food", output)
        self.assertIn("₹120.00", output)
        self.assertIn("₹150.50", output)

    def test_amount_input_retries_until_valid(self):
        with patch("builtins.input", side_effect=["oops", "0", "12.5"]):
            amount = expense_tracker.ask_for_amount()

        self.assertEqual(amount, Decimal("12.50"))


if __name__ == "__main__":
    unittest.main()
