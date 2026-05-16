import logging
import os
import time
import requests
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, g
from pythonjsonlogger import jsonlogger

# ── Structured JSON Logger ─────────────────────────────────────────────────────
logger = logging.getLogger("todo_frontend")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
))
logger.addHandler(handler)

# Silence werkzeug default logger (we replace it)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey123")
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")

# ── Request Logging ────────────────────────────────────────────────────────────
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration_ms = round((time.time() - g.start_time) * 1000, 2)
    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(level, "request_completed", extra={
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    })
    return response

# ── API Helpers ────────────────────────────────────────────────────────────────
def api_get(path, **kwargs):
    try:
        start = time.time()
        resp = requests.get(f"{API_BASE_URL}{path}", **kwargs)
        duration_ms = round((time.time() - start) * 1000, 2)
        resp.raise_for_status()
        logger.debug("api_call_success", extra={"method": "GET", "path": path, "status": resp.status_code, "duration_ms": duration_ms})
        return resp.json()
    except requests.exceptions.ConnectionError:
        logger.error("api_connection_error", extra={"method": "GET", "path": path, "api_url": API_BASE_URL})
        return None
    except requests.exceptions.HTTPError as e:
        logger.warning("api_http_error", extra={"method": "GET", "path": path, "status": e.response.status_code if e.response else "unknown"})
        return None

def api_post(path, json=None, method="POST"):
    try:
        start = time.time()
        fn = getattr(requests, method.lower())
        resp = fn(f"{API_BASE_URL}{path}", json=json)
        duration_ms = round((time.time() - start) * 1000, 2)
        resp.raise_for_status()
        logger.debug("api_call_success", extra={"method": method, "path": path, "status": resp.status_code, "duration_ms": duration_ms})
        return resp.json() if resp.content else {}
    except requests.exceptions.ConnectionError:
        logger.error("api_connection_error", extra={"method": method, "path": path, "api_url": API_BASE_URL})
        return None
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        logger.warning("api_http_error", extra={"method": method, "path": path, "status": e.response.status_code if e.response else "unknown", "detail": detail})
        raise ValueError(detail)

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    todos = api_get("/todos", params={"limit": 200})
    if todos is None:
        flash("Could not connect to the API. Please try again later.", "danger")
        todos = []

    today = date.today().isoformat()
    for todo in todos:
        if todo.get("due_date") and not todo.get("is_completed"):
            todo["is_overdue"] = todo["due_date"] < today
        else:
            todo["is_overdue"] = False

    total = len(todos)
    pending = sum(1 for t in todos if not t["is_completed"])
    completed = sum(1 for t in todos if t["is_completed"])
    logger.info("index_rendered", extra={"total": total, "pending": pending, "completed": completed})

    return render_template("index.html", todos=todos, total=total, pending=pending, completed=completed)

@app.route("/todos/new", methods=["GET"])
def new_todo():
    return render_template("todo_form.html", todo=None, action=url_for("create_todo"))

@app.route("/todos/new", methods=["POST"])
def create_todo():
    data = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip() or None,
        "due_date": request.form.get("due_date") or None,
        "priority": request.form.get("priority", "medium"),
    }
    if not data["title"]:
        flash("Title is required.", "danger")
        return render_template("todo_form.html", todo=None, action=url_for("create_todo"))
    try:
        api_post("/todos", json=data)
        logger.info("todo_create_requested", extra={"title": data["title"], "priority": data["priority"]})
        flash("Todo created successfully!", "success")
    except ValueError as e:
        logger.warning("todo_create_failed", extra={"error": str(e)})
        flash(f"Error creating todo: {e}", "danger")
        return render_template("todo_form.html", todo=None, action=url_for("create_todo"))
    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/edit", methods=["GET"])
def edit_todo(todo_id):
    todo = api_get(f"/todos/{todo_id}")
    if todo is None:
        flash("Todo not found.", "danger")
        return redirect(url_for("index"))
    return render_template("todo_form.html", todo=todo, action=url_for("update_todo", todo_id=todo_id))

@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def update_todo(todo_id):
    is_completed = request.form.get("is_completed") == "on"
    data = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip() or None,
        "due_date": request.form.get("due_date") or None,
        "priority": request.form.get("priority", "medium"),
        "is_completed": is_completed,
        "completed_date": request.form.get("completed_date") or None,
    }
    if not data["title"]:
        flash("Title is required.", "danger")
        todo = api_get(f"/todos/{todo_id}")
        return render_template("todo_form.html", todo=todo, action=url_for("update_todo", todo_id=todo_id))
    try:
        api_post(f"/todos/{todo_id}", json=data, method="PUT")
        logger.info("todo_update_requested", extra={"todo_id": todo_id})
        flash("Todo updated successfully!", "success")
    except ValueError as e:
        logger.warning("todo_update_failed", extra={"todo_id": todo_id, "error": str(e)})
        flash(f"Error updating todo: {e}", "danger")
        todo = api_get(f"/todos/{todo_id}")
        return render_template("todo_form.html", todo=todo, action=url_for("update_todo", todo_id=todo_id))
    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    try:
        resp = requests.delete(f"{API_BASE_URL}/todos/{todo_id}")
        if resp.status_code in (200, 204):
            logger.info("todo_delete_requested", extra={"todo_id": todo_id})
            flash("Todo deleted.", "success")
        else:
            logger.warning("todo_delete_failed", extra={"todo_id": todo_id, "status": resp.status_code})
            flash("Could not delete todo.", "danger")
    except requests.exceptions.ConnectionError:
        logger.error("api_connection_error", extra={"method": "DELETE", "path": f"/todos/{todo_id}"})
        flash("Could not connect to the API.", "danger")
    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/complete", methods=["POST"])
def complete_todo(todo_id):
    try:
        api_post(f"/todos/{todo_id}/complete", method="PATCH")
        logger.info("todo_completed", extra={"todo_id": todo_id})
        flash("Todo marked as complete!", "success")
    except ValueError as e:
        logger.warning("todo_complete_failed", extra={"todo_id": todo_id, "error": str(e)})
        flash(f"Error: {e}", "danger")
    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/incomplete", methods=["POST"])
def incomplete_todo(todo_id):
    try:
        api_post(f"/todos/{todo_id}/incomplete", method="PATCH")
        logger.info("todo_marked_incomplete", extra={"todo_id": todo_id})
        flash("Todo marked as incomplete.", "info")
    except ValueError as e:
        logger.warning("todo_incomplete_failed", extra={"todo_id": todo_id, "error": str(e)})
        flash(f"Error: {e}", "danger")
    return redirect(url_for("index"))

if __name__ == "__main__":
    logger.info("frontend_starting", extra={"port": 5000, "api_url": API_BASE_URL})
    app.run(host="0.0.0.0", port=5000, debug=False)

