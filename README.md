# To-Do List Web App

A Flask web app built from your original console To-Do List script. Same core
behavior (add, view, complete, remove tasks), now with a browser UI, plus
task editing.

## Folder structure

```
todo-app/
├── app.py                 # Flask backend (API + serves the page)
├── requirements.txt
├── templates/
│   └── index.html         # Page structure
└── static/
    ├── css/style.css       # Styling (responsive)
    └── js/script.js        # Talks to the Flask API, updates the UI
```

## How it maps to your original code

| Original CLI option        | Web equivalent                          |
|-----------------------------|------------------------------------------|
| 1. Add Task                 | Type in the input box, click "Add Task" |
| 2. View Task                | Tasks always shown as cards on the page |
| 3. Remove Task               | 🗑️ button on each task card             |
| 4. Mark Task as Completed   | Click the circle checkbox               |
| (not in original)            | ✏️ Edit button — lets you rename a task |

Tasks are stored in memory in a Python list (`tasks = []`), exactly like your
original script — so restarting the server clears them. There's no database,
by design, to keep this simple to run.

## 1. Install dependencies

Requires Python 3.8+. From inside the `todo-app` folder:

```bash
pip install -r requirements.txt
```

(Optional but recommended: use a virtual environment first)

```bash
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Run the app

```bash
python app.py
```

You'll see output like:

```
 * Running on http://127.0.0.1:5000
```

## 3. Open it in your browser

Go to: **http://127.0.0.1:5000**

That's it — add, complete, edit, and delete tasks right from the page.

## Notes

- Data resets whenever you restart `app.py` (in-memory only, like the
  original script). If you want tasks to persist across restarts later,
  the natural next step is swapping the `tasks` list for a small SQLite
  database — happy to add that if you want it.
- To stop the server, press `Ctrl+C` in the terminal.
