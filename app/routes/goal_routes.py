from flask import Blueprint, request
from app.routes.route_utilities import create_model, get_models_with_filters, validate_model, create_no_content_response
from ..db import db
from app.models.goal import Goal
from app.models.task import Task


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.post("")
def create_goal():
    request_body = request.get_json()
    return create_model(Goal, request_body)

@goals_bp.get("")
def get_all_goals():
    title_param = request.args.get("title")
    filters = {}
    if title_param:
        filters["title"] = title_param

    goals_response = get_models_with_filters(Goal, filters)
    return goals_response

@goals_bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return goal.to_dict()

@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return goal.to_dict()

@goals_bp.post("/<goal_id>/tasks")
def post_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])

    current_tasks = db.session.scalars(db.select(Task).where(Task.goal_id == goal.id)).all()
    for task in current_tasks:
        if task.id not in task_ids:
            task.goal_id = None

    if task_ids:
        tasks = db.session.scalars(db.select(Task).where(Task.id.in_(task_ids))).all()
        for task in tasks:
            task.goal_id = goal.id

    db.session.commit()

    return {"id": goal.id, "task_ids": task_ids}


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    tasks = db.session.scalars(db.select(Task).where(Task.goal_id == goal.id))
    tasks_list = []
    for task in tasks:
        task_dict = task.to_dict()
        task_dict["goal_id"] = task.goal_id
        tasks_list.append(task_dict)

    response = goal.to_dict()
    response["tasks"] = tasks_list
    return response

@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()

    return create_no_content_response()