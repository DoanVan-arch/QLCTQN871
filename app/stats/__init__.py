from flask import Blueprint

bp = Blueprint("stats", __name__, url_prefix="/thong-ke")

from app.stats import routes  # noqa: E402,F401
