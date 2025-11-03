from flask import Blueprint, Response, abort, make_response, request
from app.routes.route_utilities import validate_model
from app.models.task import Task
from flask import Blueprint
from ..db import db

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)

    except KeyError as error:
        response = {"message": f"Invalid request: missing {error.args[0]}"}
        abort(make_response(response, 400))

    db.session.add(new_task)
    db.session.commit()

    return new_task.to_dict(), 201


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    book = validate_model(Task, task_id)
    return book.to_dict()