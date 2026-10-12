# Python Expense Tracker

A small command-line project that now introduces the Python tools you will genuinely use in interview questions and real programs. It needs only Python 3.

```bash
cd python-expense-tracker
python3 expense_tracker.py
python3 -m unittest -v
```

## Project map

```
expense_tracker.py  # menu, input, printing, summary calculations
models.py           # Transaction and Expense classes
storage.py          # JSON file reading and writing
expenses.json       # your data; created after the first expense
test_expense_tracker.py
```

## Concepts to study here

| Concept | Where to read it | Why it is here |
| --- | --- | --- |
| `class`, `self`, `__init__` | `models.py` | `@dataclass` generates `__init__`; every instance method receives `self` explicitly. |
| `__str__`, `__repr__`, `__eq__` | `models.py` | We define readable printing; dataclass generates value-based `__eq__`. Try `print(expense)` and `[expense]`. |
| Inheritance and `super()` | `Transaction` → `Expense` | An expense is a transaction with category and amount. |
| `@dataclass` | `Expense` | Fields turn into an initializer and equality method without boilerplate. |
| `@staticmethod` | `Expense.parse_amount` | Validates text without needing an object. |
| `@classmethod` | `Expense.from_dict` | Creates an object from saved data; `cls` supports subclasses. |
| Modules and imports | all three Python files | The app imports `Expense`; storage imports it too. |
| Type hints | function signatures | Helpful editor/documentation clues, but Python does not enforce them at runtime. |
| `if __name__ == "__main__"` | bottom of `expense_tracker.py` | Starts the app only when run directly—not when a test imports it. |
| `Counter` | `show_summary()` | Counts expenses per category in one line. |
| `defaultdict` | `show_summary()` | Starts every category total at zero automatically. |
| `sorted(..., key=..., reverse=True)` | `show_summary()` | Sorts categories by largest total. |
| `heapq.nlargest` | `show_summary()` | Finds the three biggest expenses using a heap. |
| `sum`, `min`, `max` | `show_summary()` | Total spending and highest/lowest expense. |
| `json.loads` / `json.dumps` | `storage.py` | Convert JSON text ↔ Python data. |
| `with open(...)` | `storage.py` | Opens files safely and closes them automatically. |

## A useful way to explore

Start the program, add three expenses in two categories, then choose **View summary**. Next, open `expenses.json`: it is a list of dictionaries. Follow the path backwards:

`JSON text` → `json.loads` → `Expense.from_dict` → `Expense objects` → summary calculations.

Then follow saving in the other direction:

`Expense objects` → `to_dict` → `json.dumps` → `JSON text`.

## Two concepts not forced into this app

`deque` is excellent for a queue/BFS, but an expense tracker has no graph traversal or queue. `float("inf")` is usually a starting value for a “smallest distance so far” algorithm; normal `min()` is clearer here. Learn both in a short separate exercise instead:

```python
from collections import deque

queue = deque(["start"])
visited = set()
best_distance = float("inf")

while queue:
    node = queue.popleft()  # fast removal from the left: perfect for BFS
    if node not in visited:
        visited.add(node)
        # queue.append(each_neighbor)
```

`any()` and `all()` are also best when there is a real question to ask. Add this after loading expenses to experiment:

```python
has_food = any(expense.category == "Food" for expense in expenses)
all_positive = all(expense.amount > 0 for expense in expenses)
```

## Next challenge

Implement a budget feature: ask for a monthly budget, calculate `budget - total_spent`, and print a warning with `any()` if any one expense is bigger than half the budget.
