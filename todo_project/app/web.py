from flask import Blueprint, flash, redirect, render_template, request, url_for

from .extensions import db
from .models import Todo


web = Blueprint("web", __name__)


def clean_title(value):
    return (value or "").strip()


def find_todo(todo_id):
    return db.session.get(Todo, todo_id)


@web.get("/")
def index():
    todos = db.session.execute(
        db.select(Todo).order_by(Todo.completed.asc(), Todo.id.desc())
    ).scalars().all()
    return render_template("index.html", todos=todos)


@web.post("/todos")
def create_todo():
    title = clean_title(request.form.get("title"))
    if not title or len(title) > 200:
        flash("A title between 1 and 200 characters is required.", "error")
        return redirect(url_for("web.index"))

    db.session.add(Todo(title=title))
    db.session.commit()
    flash("Todo created.", "success")
    return redirect(url_for("web.index"))


@web.post("/todos/<int:todo_id>/toggle")
def toggle_todo(todo_id):
    todo = find_todo(todo_id)
    if todo is None:
        return render_template("404.html"), 404

    todo.completed = not todo.completed
    todo.touch()
    db.session.commit()
    return redirect(url_for("web.index"))


@web.get("/todos/<int:todo_id>/edit")
def edit_todo(todo_id):
    todo = find_todo(todo_id)
    if todo is None:
        return render_template("404.html"), 404
    return render_template("edit.html", todo=todo)


@web.post("/todos/<int:todo_id>/edit")
def update_todo(todo_id):
    todo = find_todo(todo_id)
    if todo is None:
        return render_template("404.html"), 404

    title = clean_title(request.form.get("title"))
    if not title or len(title) > 200:
        flash("A title between 1 and 200 characters is required.", "error")
        return redirect(url_for("web.edit_todo", todo_id=todo_id))

    todo.title = title
    todo.touch()
    db.session.commit()
    flash("Todo updated.", "success")
    return redirect(url_for("web.index"))


@web.post("/todos/<int:todo_id>/delete")
def delete_todo(todo_id):
    todo = find_todo(todo_id)
    if todo is None:
        return render_template("404.html"), 404

    db.session.delete(todo)
    db.session.commit()
    flash("Todo deleted.", "success")
    return redirect(url_for("web.index"))
