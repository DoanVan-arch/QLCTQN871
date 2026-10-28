# -*- coding: utf-8 -*-
import os

from flask import Flask

from app.extensions import db, login_manager
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.personnel import bp as personnel_bp
    from app.settings import bp as settings_bp
    from app.stats import bp as stats_bp
    from app.users import bp as users_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(personnel_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(settings_bp)

    from app.utils.constants import CATEGORY_CHOICES, ROLE_LABELS

    @app.context_processor
    def inject_globals():
        return {
            "nav_categories": CATEGORY_CHOICES,
            "role_labels": ROLE_LABELS,
        }

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user

        if not current_user.is_authenticated:
            return {}
        from app.utils.notifications import notification_feed

        try:
            return {"notification_summary": notification_feed()}
        except Exception:
            return {"notification_summary": {"entries": [], "total": 0}}

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template

        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template

        return render_template("errors/404.html"), 404

    with app.app_context():
        db.create_all()
        _ensure_schema_upgrades()
        _ensure_default_admin()

    return app


def _ensure_schema_upgrades():
    """Tu dong them cac cot moi vao bang personnel neu CSDL cu chua co (SQLite)."""
    from sqlalchemy import text

    new_columns = {
        "reward_evidence_file": "VARCHAR(255)",
        "archived_from_category": "VARCHAR(30)",
        "archived_at": "DATETIME",
    }
    with db.engine.connect() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(personnel)"))}
        for col_name, col_type in new_columns.items():
            if col_name not in existing:
                conn.execute(text(f"ALTER TABLE personnel ADD COLUMN {col_name} {col_type}"))
        conn.commit()


def _ensure_default_admin():
    """Tao san tai khoan admin mac dinh neu CSDL chua co tai khoan nao."""
    from app.models import User
    from app.utils.constants import ROLE_ADMIN

    if User.query.count() == 0:
        admin = User(
            username="admin",
            full_name="Quản trị viên hệ thống",
            role=ROLE_ADMIN,
            is_active_account=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
