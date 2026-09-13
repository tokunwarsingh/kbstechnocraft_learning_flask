from flask import Blueprint, request

from .extensions import db
from .models import Todo


api = Blueprint("api", __name__, url_prefix="/api")


def parse_json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, ({"error": "Request body must be a JSON object"}, 400)
    return data, None


def validate_title(value):
    if not isinstance(value, str):
        return None
    title = value.strip()
    if not title or len(title) > 200:
        return None
    return title


@api.get("/todos")
def list_todos():
    todos = db.session.execute(
        db.select(Todo).order_by(Todo.completed.asc(), Todo.id.desc())
    ).scalars().all()
    return {"items": [todo.to_dict() for todo in todos]}


@api.post("/todos")
def create_todo():
    data, error = parse_json_body()
    if error:
        return error

    title = validate_title(data.get("title"))
    if title is None:
        return {"error": "title must be 1 to 200 characters"}, 400

    todo = Todo(title=title)
    db.session.add(todo)
    db.session.commit()
    return todo.to_dict(), 201


@api.patch("/todos/<int:todo_id>")
def update_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return {"error": "Todo not found"}, 404

    data, error = parse_json_body()
    if error:
        return error

    if "title" in data:
        title = validate_title(data["title"])
        if title is None:
            return {"error": "title must be 1 to 200 characters"}, 400
        todo.title = title

    if "completed" in data:
        if not isinstance(data["completed"], bool):
            return {"error": "completed must be a boolean"}, 400
        todo.completed = data["completed"]

    todo.touch()
    db.session.commit()
    return todo.to_dict()


@api.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return {"error": "Todo not found"}, 404

    db.session.delete(todo)
    db.session.commit()
    return "", 204
