"""
To-Do List web application (Flask backend), backed by SQLite.

Route mapping to the original console script:
  - "Add Task"      -> POST   /api/tasks
  - "View Task"     -> GET    /api/tasks
  - "Remove Task"   -> DELETE /api/tasks/<id>
  - "Mark Complete" -> POST   /api/tasks/<id>/toggle
  - "Edit Task" (new, not in the console version) -> PUT /api/tasks/<id>

Tasks are now stored in a SQLite database file (todo.db) instead of an
in-memory list, so they persist across restarts and server sleeps
(important on free hosting tiers like Render, which spin the app down
after inactivity). The database file is created automatically the first
time the app runs.
"""

import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request, render_template, g

app = Flask(__name__)

DB_PATH = Path(__file__).parent / "todo.db"


def get_db():
    """Open (or reuse) a SQLite connection for the current request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the tasks table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def row_to_task(row):
    return {"id": row["id"], "text": row["text"], "completed": bool(row["completed"])}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Equivalent of choice '2' (View Task)."""
    db = get_db()
    rows = db.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return jsonify([row_to_task(r) for r in rows])


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Equivalent of choice '1' (Add Task)."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Task text cannot be empty."}), 400

    db = get_db()
    cur = db.execute("INSERT INTO tasks (text, completed) VALUES (?, 0)", (text,))
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(row_to_task(row)), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    """Edit a task's text (extension of the original CLI)."""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Task text cannot be empty."}), 400

    db = get_db()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Task not found."}), 404

    db.execute("UPDATE tasks SET text = ? WHERE id = ?", (text, task_id))
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return jsonify(row_to_task(row))


@app.route("/api/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """Equivalent of choice '4' (Mark Task as Completed) - toggles the
    completed flag, matching the original's check for whether it was
    already marked done."""
    db = get_db()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Task not found."}), 404

    new_value = 0 if row["completed"] else 1
    db.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_value, task_id))
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return jsonify(row_to_task(row))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Equivalent of choice '3' (Remove Task)."""
    db = get_db()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Task not found."}), 404

    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return jsonify({"message": "Removed", "task": row_to_task(row)})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
