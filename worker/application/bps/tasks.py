from flask import Blueprint, request, jsonifyfrom application import celerybp_tasks = Blueprint("bp_tasks", __name__, url_prefix="/task")@bp_tasks.route("/start", methods=["GET"])def start_task():    resd = {"status": "ok"}    task_name = request.args["task_name"]    args = request.json.get("args", None)    kwargs = request.json.get("kwargs", None)    extra = request.json.get("extra", dict())    task_id = celery.send_task(task_name, args, kwargs, **extra)    resd["task_id"] = task_id    return jsonify(resd), 202