from flask import Blueprint, Response, abort, make_response, request
from app.routes.route_utilities import create_model, validate_model, get_models_with_filters, create_no_content_response
from app.models.task import Task
from flask import Blueprint
from ..db import db
import os
import requests

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()
    return create_model(Task, request_body)

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))

    description_param = request.args.get("description")
    if description_param:
        query = query.where(Task.description.ilike(f"%{description_param}%"))

    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Task.title)
    elif sort_param == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.id)

    tasks = db.session.scalars(query)

    tasks_response = []
    for book in tasks:
        tasks_response.append(book.to_dict())
    return tasks_response


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict()

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    book = validate_model(Task, task_id)
    request_body = request.get_json()

    book.title = request_body["title"]
    book.description = request_body["description"]
    db.session.commit()

    return create_no_content_response()

@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    return create_no_content_response()

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = db.func.now()
    db.session.commit()
    # send a notification to Slack
    # reference:https://docs.slack.dev/tools/python-slack-sdk/legacy/basic_usage/
    try:
        slack_token = os.environ.get("SLACK_API_TOKEN")
        headers = {"Authorization": f"Bearer {slack_token}"} if slack_token else {}
        message = {
            "channel": "task-notifications",
            "text": f"Someone just completed the task {task.title}"
        }
        
        requests.post("https://slack.com/api/chat.postMessage", json=message, headers=headers)
    except Exception:
        pass

    return create_no_content_response()

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()

    return create_no_content_response()

