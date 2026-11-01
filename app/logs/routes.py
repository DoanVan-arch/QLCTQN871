# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from flask import render_template, request
from flask_login import login_required
from sqlalchemy import or_

from app.decorators import admin_required
from app.logs import bp
from app.models import ActivityLog
from app.utils.activity import ACTION_LABELS


@bp.route("/")
@login_required
@admin_required
def index():
    q = request.args.get("q", "").strip()
    action = request.args.get("action", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    page = request.args.get("page", 1, type=int)

    query = ActivityLog.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                ActivityLog.username.ilike(like),
                ActivityLog.target.ilike(like),
                ActivityLog.details.ilike(like),
                ActivityLog.ip_address.ilike(like),
            )
        )
    if action:
        query = query.filter(ActivityLog.action == action)
    try:
        if date_from:
            query = query.filter(ActivityLog.created_at >= datetime.strptime(date_from, "%Y-%m-%d"))
        if date_to:
            query = query.filter(
                ActivityLog.created_at < datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            )
    except ValueError:
        pass

    pagination = query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template(
        "logs/index.html",
        pagination=pagination,
        logs=pagination.items,
        action_labels=ACTION_LABELS,
        q=q,
        action=action,
        date_from=date_from,
        date_to=date_to,
    )
