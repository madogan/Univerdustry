from flask import Blueprint, jsonify, url_for, requestfrom application.tasks.download_pdf import task_download_pdffrom application.tasks.pdf_to_text import task_pdf_to_text_by_file_pathfrom werkzeug.exceptions import BadRequesttasks_bp = Blueprint("tasks_bp", __name__)@tasks_bp.route("/pdf_to_text_by_file_path", methods=["GET"])def r_task_pdf_to_text_by_file_path():    file_path = request.args.get("file_path", None)    if not file_path:        raise BadRequest    task = task_pdf_to_text_by_file_path.apply_async(        kwargs={"file_path": file_path}    )    return (jsonify({"status": "ok", "message": "Added to queue."}), 202,            {"Location": url_for("tasks_bp.check_task_status",                                 task_name="pdf_to_text_by_file_path",                                 task_id=task.id)})@tasks_bp.route("/download_pdf", methods=["GET"])def r_task_download_pdf():    url = request.args.get("url", None)    if not url:        raise BadRequest    task = task_download_pdf.apply_async(        kwargs={"url": url}    )    return (jsonify({"status": "ok", "message": "Added to queue."}), 202,            {"Location": url_for("tasks_bp.check_task_status",                                 task_name="download_pdf", task_id=task.id)})@tasks_bp.route("/<task_name>/status/<task_id>", methods=["GET"])def check_task_status(task_name, task_id):    task = globals()["task_" + task_name].AsyncResult(task_id)    if task.state == "PENDING":        # job did not start yet        response = {            "state": task.state,            "current": 0,            "total": 1,            "status": task.state.lower()        }    elif task.state != "FAILURE":        response = {            "state": task.state,            "current": task.info.get("current", 0),            "total": task.info.get("total", 1),            "status": task.info.get("status", "").lower()        }        if "result" in task.info:            response["result"] = task.info["result"]    else:        # something went wrong in the background job        response = {            "state": task.state,            "current": 1,            "total": 1,            "status": str(task.info),  # this is the exception raised        }    return jsonify(response)