from flask import Blueprint

bp = Blueprint("personnel", __name__, url_prefix="/quan-ly/<category>")

from app.personnel import routes  # noqa: E402,F401
