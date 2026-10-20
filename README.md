# StatsMatch

Local Flask app with fictional data in `data/mock_players.csv`.

## Run in PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000. Press Ctrl+C to stop.

## File organization

- `app.py`: starts the server.
- `app/__init__.py`: creates Flask and registers routes.
- `app/routes/search.py`: search screen Python logic.
- `app/routes/detail.py`: detail screen Python logic and per-90 calculations.
- `app/services/players.py`: shared CSV loading.
- `app/templates/search.html`: search screen HTML.
- `app/templates/detail.html`: player detail HTML.
- `app/templates/base.html`: shared header
- `app/templates/not_found.html`: missing page/player message.
- `app/static/css/style.css`: shared styling.
