# Python Expense Tracker

A beginner-friendly command-line program for recording what you spend. It uses only the Python standard library, so it works with a normal Python 3 installation.

## Run it

Open a terminal in this folder and run:

```bash
python3 expense_tracker.py
```

Choose an option from the menu. Your entries are saved automatically in `expenses.json`, which the program creates after your first expense. That file is deliberately ignored by the program's source code: it is your data, not part of the code.

## Try this first

1. Add `Lunch`, category `Food`, amount `150`.
2. Add `Metro`, category `Travel`, amount `42.50`.
3. Choose **View expenses** to see a table.
4. Choose **View summary** to see totals grouped by category.
5. Quit and run the program again—the entries should still be there.

## How the program is put together

| Part | What it teaches |
| --- | --- |
| `main()` | A `while True` loop, menu choices, and `if` / `elif` / `else` |
| `add_expense()` | Reading input, creating dictionaries, and adding to a list with `append()` |
| `print_expenses()` | Loops, `enumerate()`, f-strings, and table formatting |
| `show_summary()` | Dictionaries as category totals and arithmetic with `Decimal` |
| `load_expenses()` / `save_expenses()` | Reading and writing JSON files |
| `try` / `except` | Gracefully handling invalid input instead of crashing |

An expense is represented as a dictionary:

```python
{
    "title": "Lunch",
    "category": "Food",
    "amount": "150.00",
    "date": "2026-10-11"
}
```

All expenses live together in a Python list. JSON saves that list so the data remains after the program stops.

## Why `Decimal` for money?

Computers store ordinary floating-point numbers approximately. For example, `0.1 + 0.2` can produce a tiny rounding error. `Decimal` is designed for exact base-10 values such as currency, so the tracker uses it when calculating amounts.

## Run the tests

The project includes two small tests. They check the summary calculation and invalid amount handling:

```bash
python3 -m unittest -v
```

## Experiments to try next

- Add a **monthly budget** and show money remaining.
- Let the user filter the expense list by a category.
- Ask for a custom date instead of always using today.
- Add an `income` field and show a balance.
- Change the currency symbol in the f-strings.

When you make a change, run the tests again. If something breaks, that is useful feedback: read the traceback from bottom to top, find the line in your code, and fix one small thing at a time.
# python-expense-tracker
