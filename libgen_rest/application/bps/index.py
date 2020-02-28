from flask import Blueprint

index_bp = Blueprint("index_bp", __name__)


@index_bp.route("/", defaults={"path": ""})
@index_bp.route("/<path:path>")
def index(path):
    return "Running..."
