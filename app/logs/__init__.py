from flask import Blueprint

bp = Blueprint("logs", __name__, url_prefix="/logs")

from app.logs import routes  # noqa: E402,F401
