"""
To-Do List web application (Flask backend).

This mirrors the logic of the original console script:
  - tasks are stored in memory in a list
  - "Add Task"      -> POST   /api/tasks
  - "View Task"     -> GET    /api/tasks
  - "Remove Task"   -> DELETE /api/tasks/<id>
  - "Mark Complete" -> POST   /api/tasks/<id>/toggle   (toggles, like the
                                                          original's "already
                                                          completed" check)
  - "Edit Task" (new, not in the console version) -> PUT /api/tasks/<id>

Instead of appending a "✓" to the string (which was fine for a terminal
printout but awkward for a UI), each task is now a small dict:
    {"id": int, "text": str, "completed": bool}
The *behavior* is identical to the original: a task starts incomplete,
can be marked completed, toggled back, edited, or removed. Data lives only
in memory, exactly like the original `tasks = []` list, so it resets when
the server restarts.
"""

from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# In-memory storage - equivalent to the original `tasks = []`
tasks = []
next_id = 1  # simple auto-incrementing id, since a plain list has no stable id


def find_task(task_id):
    """Return the task dict with this id, or None."""
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Equivalent of choice '2' (View Task)."""
    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Equivalent of choice '1' (Add Task)."""
    global next_id
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Task text cannot be empty."}), 400

    task = {"id": next_id, "text": text, "completed": False}
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    """Edit a task's text (extension of the original CLI)."""
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Task text cannot be empty."}), 400

    task["text"] = text
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """Equivalent of choice '4' (Mark Task as Completed) - toggles the
    completed flag, matching the original's check for whether it was
    already marked done."""
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    task["completed"] = not task["completed"]
    return jsonify(task)


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Equivalent of choice '3' (Remove Task)."""
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found."}), 404

    tasks.remove(task)
    return jsonify({"message": "Removed", "task": task})


if __name__ == "__main__":
    app.run(debug=True)
