"""The command-line interface for the expense tracker."""

from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
import heapq

from models import Expense
from storage import load_expenses, save_expenses


def ask_for_amount() -> Decimal:
    """Keep asking until Expense.parse_amount accepts the answer."""
    while True:
        try:
            return Expense.parse_amount(input("Amount: ₹").strip())
        except ValueError as error:
            print(error)


def add_expense(expenses: list[Expense]) -> None:
    print("\n--- Add an expense ---")
    expense = Expense(
        title=input("What did you buy? "),
        category=input("Category (food, travel, bills...): "),
        amount=ask_for_amount(),
        date=date.today().isoformat(),
    )
    expenses.append(expense)
    save_expenses(expenses)
    print("Expense saved!\n")


def print_expenses(expenses: list[Expense]) -> None:
    if not expenses:
        print("\nNo expenses yet. Choose option 1 to add one.\n")
        return

    print("\n--- Your expenses ---")
    print(f"{'#':<4}{'Date':<12}{'Category':<16}{'Title':<25}{'Amount':>12}")
    print("-" * 69)
    for number, expense in enumerate(expenses, start=1):
        print(f"{number:<4}{expense.date:<12}{expense.category:<16}{expense.title:<25}₹{expense.amount:>10.2f}")
    print()


def show_summary(expenses: list[Expense]) -> None:
    if not expenses:
        print("\nNo expenses to summarize yet.\n")
        return

    # defaultdict creates Decimal('0') automatically for new categories.
    totals_by_category: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for expense in expenses:
        totals_by_category[expense.category] += expense.amount

    # Counter counts how many expenses each category contains in one line.
    expense_count = Counter(expense.category for expense in expenses)
    total_spent = sum((expense.amount for expense in expenses), start=Decimal("0"))
    highest = max(expenses, key=lambda expense: expense.amount)
    lowest = min(expenses, key=lambda expense: expense.amount)

    print("\n--- Spending summary ---")
    # The key function says "sort by the total"; reverse=True puts largest first.
    for category, total in sorted(totals_by_category.items(), key=lambda item: item[1], reverse=True):
        print(f"{category:<16} ₹{total:.2f} ({expense_count[category]} expense(s))")

    print(f"{'TOTAL':<16} ₹{total_spent:.2f}")
    print(f"Highest: {highest.title} (₹{highest.amount:.2f})")
    print(f"Lowest:  {lowest.title} (₹{lowest.amount:.2f})")

    # heapq.nlargest uses a heap internally. This is useful when the list is huge.
    top_expenses = heapq.nlargest(3, expenses, key=lambda expense: expense.amount)
    print("Top expenses:", ", ".join(expense.title for expense in top_expenses), "\n")


def delete_expense(expenses: list[Expense]) -> None:
    if not expenses:
        print("\nThere is nothing to delete.\n")
        return

    print_expenses(expenses)
    try:
        number = int(input("Enter an expense number to delete (or 0 to cancel): "))
        if number == 0:
            return
        removed_expense = expenses.pop(number - 1)
        save_expenses(expenses)
        print(f"Deleted: {removed_expense.title}\n")
    except (ValueError, IndexError):
        print("That is not a valid expense number. Nothing was deleted.\n")


def main() -> None:
    """Run the menu until option 5 returns from this function."""
    expenses = load_expenses()

    while True:
        print("Expense Tracker")
        print("1. Add expense\n2. View expenses\n3. View summary\n4. Delete expense\n5. Quit")
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


# Importing this file in a test will not start the menu. Executing it will.
if __name__ == "__main__":
    main()
