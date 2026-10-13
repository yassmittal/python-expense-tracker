# Expense Tracker — FastAPI version

The same expense tracker as the CLI one level up, rebuilt as a web API.

## Run it

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000/docs, click an endpoint → **Try it out** → **Execute**.

## Files (suggested order to write them by hand)

```
schemas.py         # 1. Pydantic models: what goes in and out (replaces models.py)
list_storage.py    # 2. Store expenses in a Python list (lost on restart)
main.py            # 3. The FastAPI app and all routes
sqlite_storage.py  # 4. Stretch: same functions, but saved in expenses.db
```

Start with `import list_storage as storage` in `main.py`, get every endpoint working,
then write `sqlite_storage.py` and switch that one import line.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/expenses` | List all expenses. Add `?category=food` to filter. |
| GET | `/expenses/{expense_id}` | One expense, or **404** if it does not exist. |
| POST | `/expenses` | Create one. Body is validated by `ExpenseCreate` (amount must be > 0). Returns **201**. |
| DELETE | `/expenses/{expense_id}` | Delete one. Returns **204** (empty), or **404**. |
| GET | `/summary` | Totals per category, highest, lowest, top three. |

## Things to try in /docs

1. POST `{"title": "Lunch", "category": "Food", "amount": 120}`. You get back an `id` and today's `date`.
2. POST with `"amount": 0` or `"amount": "abc"`. Read the **422** error. You never wrote that check yourself!
3. GET `/expenses/999`. You get the **404** you raised with `HTTPException`.
4. GET `/expenses/abc`. You get a **422** because `expense_id: int` is not a number.
5. Using `list_storage`: save `main.py` (the server reloads) and GET `/expenses`. Everything is gone.
   Using `sqlite_storage`: your data survives the reload.

## CLI → API, side by side

| CLI (`expense_tracker.py`) | API (`api/main.py`) |
| --- | --- |
| Menu option chosen with `input()` | HTTP method + URL path |
| `ask_for_amount()` while-loop | `Field(gt=0)` + automatic 422 |
| `print("not a valid number")` | `raise HTTPException(404, ...)` |
| `print(...)` the summary | `return Summary(...)` → JSON |
| `storage.py` JSON file | `list_storage.py` / `sqlite_storage.py` |
