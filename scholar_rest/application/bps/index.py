from flask import Blueprint

bp_index = Blueprint("bp_index", __name__)


@bp_index.route("/", defaults={"path": ""})
@bp_index.route("/<path:path>")
def index(path):
    return "Running..."
