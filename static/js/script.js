const API = "/api/tasks";

const taskList = document.getElementById("task-list");
const emptyState = document.getElementById("empty-state");
const statsEl = document.getElementById("stats");
const addForm = document.getElementById("add-task-form");
const taskInput = document.getElementById("task-input");
const filterButtons = document.querySelectorAll(".filter-btn");

const editModal = document.getElementById("edit-modal");
const editInput = document.getElementById("edit-input");
const editSaveBtn = document.getElementById("edit-save");
const editCancelBtn = document.getElementById("edit-cancel");

let tasks = [];
let currentFilter = "all";
let editingTaskId = null;

async function fetchTasks() {
  const res = await fetch(API);
  tasks = await res.json();
  render();
}

async function addTask(text) {
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (res.ok) {
    const task = await res.json();
    tasks.push(task);
    render();
  }
}

async function toggleTask(id) {
  const res = await fetch(`${API}/${id}/toggle`, { method: "POST" });
  if (res.ok) {
    const updated = await res.json();
    const idx = tasks.findIndex((t) => t.id === id);
    tasks[idx] = updated;
    render();
  }
}

async function deleteTask(id) {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (res.ok) {
    tasks = tasks.filter((t) => t.id !== id);
    render();
  }
}

async function editTask(id, text) {
  const res = await fetch(`${API}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (res.ok) {
    const updated = await res.json();
    const idx = tasks.findIndex((t) => t.id === id);
    tasks[idx] = updated;
    render();
  }
}

function getFilteredTasks() {
  if (currentFilter === "active") return tasks.filter((t) => !t.completed);
  if (currentFilter === "completed") return tasks.filter((t) => t.completed);
  return tasks;
}

function render() {
  const filtered = getFilteredTasks();
  taskList.innerHTML = "";

  if (tasks.length === 0) {
    emptyState.hidden = false;
    emptyState.textContent = "No tasks yet — add your first one above! 🎉";
  } else if (filtered.length === 0) {
    emptyState.hidden = false;
    emptyState.textContent = "No tasks in this view.";
  } else {
    emptyState.hidden = true;
  }

  filtered.forEach((task) => {
    const li = document.createElement("li");
    li.className = "task-card";

    const checkbox = document.createElement("button");
    checkbox.className = "task-checkbox" + (task.completed ? " checked" : "");
    checkbox.setAttribute("aria-label", "Toggle complete");
    checkbox.textContent = task.completed ? "✓" : "";
    checkbox.onclick = () => toggleTask(task.id);

    const text = document.createElement("span");
    text.className = "task-text" + (task.completed ? " completed" : "");
    text.textContent = task.text;

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const editBtn = document.createElement("button");
    editBtn.className = "icon-btn";
    editBtn.title = "Edit task";
    editBtn.textContent = "✏️";
    editBtn.onclick = () => openEditModal(task);

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "icon-btn delete";
    deleteBtn.title = "Delete task";
    deleteBtn.textContent = "🗑️";
    deleteBtn.onclick = () => deleteTask(task.id);

    actions.append(editBtn, deleteBtn);
    li.append(checkbox, text, actions);
    taskList.appendChild(li);
  });

  const completedCount = tasks.filter((t) => t.completed).length;
  statsEl.textContent = tasks.length
    ? `${completedCount} of ${tasks.length} task${tasks.length !== 1 ? "s" : ""} completed`
    : "";
}

function openEditModal(task) {
  editingTaskId = task.id;
  editInput.value = task.text;
  editModal.hidden = false;
  editInput.focus();
}

function closeEditModal() {
  editingTaskId = null;
  editModal.hidden = true;
}

addForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = taskInput.value.trim();
  if (!text) return;
  addTask(text);
  taskInput.value = "";
});

filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.filter;
    render();
  });
});

editSaveBtn.addEventListener("click", () => {
  const text = editInput.value.trim();
  if (!text || editingTaskId === null) return;
  editTask(editingTaskId, text);
  closeEditModal();
});

editCancelBtn.addEventListener("click", closeEditModal);
editModal.addEventListener("click", (e) => {
  if (e.target === editModal) closeEditModal();
});
editInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") editSaveBtn.click();
  if (e.key === "Escape") closeEditModal();
});

fetchTasks();
