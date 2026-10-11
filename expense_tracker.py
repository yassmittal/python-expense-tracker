"""A tiny command-line expense tracker.

This program demonstrates functions, lists, dictionaries, loops, conditionals,
JSON files, exceptions, and formatted strings in one useful project.
"""

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


# The file is stored beside this Python program, no matter where it is run from.
DATA_FILE = Path(__file__).with_name("expenses.json")


def load_expenses():
    """Read saved expenses from JSON. Return an empty list on the first run."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        # A corrupted file should not crash a beginner's project.
        print("Could not read expenses.json. Starting with an empty list.")
        return []


def save_expenses(expenses):
    """Convert the Python list into JSON and write it to disk."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=2)


def ask_for_amount():
    """Keep asking until the user types a positive money amount."""
    while True:
        raw_amount = input("Amount: ₹").strip()
        try:
            amount = Decimal(raw_amount).quantize(Decimal("0.01"))
            if amount <= 0:
                print("Please enter an amount greater than zero.")
                continue
            return amount
        except InvalidOperation:
            print("Please enter a number, for example 125 or 49.50.")


def add_expense(expenses):
    """Ask the user for fields, create one dictionary, and save it."""
    print("\n--- Add an expense ---")
    title = input("What did you buy? ").strip()
    category = input("Category (food, travel, bills...): ").strip()
    amount = ask_for_amount()

    # JSON cannot store Decimal values, so we save the amount as a string.
    expense = {
        "title": title or "Untitled expense",
        "category": category or "Other",
        "amount": str(amount),
        "date": date.today().isoformat(),
    }
    expenses.append(expense)  # append adds one item to the end of a list
    save_expenses(expenses)
    print("Expense saved!\n")


def print_expenses(expenses):
    """Display each expense in a readable table."""
    if not expenses:
        print("\nNo expenses yet. Choose option 1 to add one.\n")
        return

    print("\n--- Your expenses ---")
    print(f"{'#':<4}{'Date':<12}{'Category':<16}{'Title':<25}{'Amount':>12}")
    print("-" * 69)
    for number, expense in enumerate(expenses, start=1):
        print(
            f"{number:<4}{expense['date']:<12}{expense['category']:<16}"
            f"{expense['title']:<25}₹{Decimal(expense['amount']):>10.2f}"
        )
    print()


def show_summary(expenses):
    """Calculate and display the total spent in every category."""
    if not expenses:
        print("\nNo expenses to summarize yet.\n")
        return

    totals_by_category = {}
    total_spent = Decimal("0")

    for expense in expenses:
        category = expense["category"]
        amount = Decimal(expense["amount"])
        total_spent += amount
        # dict.get supplies Decimal('0') when this category appears for the first time.
        totals_by_category[category] = totals_by_category.get(category, Decimal("0")) + amount

    print("\n--- Spending summary ---")
    for category, total in sorted(totals_by_category.items()):
        print(f"{category:<16} ₹{total:.2f}")
    print(f"{'TOTAL':<16} ₹{total_spent:.2f}\n")


def delete_expense(expenses):
    """Remove one expense by its displayed number."""
    if not expenses:
        print("\nThere is nothing to delete.\n")
        return

    print_expenses(expenses)
    try:
        number = int(input("Enter an expense number to delete (or 0 to cancel): "))
        if number == 0:
            return
        removed_expense = expenses.pop(number - 1)  # Lists start at index 0.
        save_expenses(expenses)
        print(f"Deleted: {removed_expense['title']}\n")
    except (ValueError, IndexError):
        print("That is not a valid expense number. Nothing was deleted.\n")


def main():
    """Run the menu until the user chooses to quit."""
    expenses = load_expenses()

    while True:  # An infinite loop; option 5 exits it with return.
        print("Expense Tracker")
        print("1. Add expense")
        print("2. View expenses")
        print("3. View summary")
        print("4. Delete expense")
        print("5. Quit")

        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            print_expenses(expenses)
        elif choice == "3":
            show_summary(expenses)
        elif choice == "4":
            delete_expense(expenses)
        elif choice == "5":
            print("Goodbye! Your expenses are saved in expenses.json.")
            return
        else:
            print("Please choose a number from 1 to 5.\n")


# This condition means main() runs only when this file is executed directly.
# It does not run when another Python file imports this one.
if __name__ == "__main__":
    main()
