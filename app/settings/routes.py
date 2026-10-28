# -*- coding: utf-8 -*-
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import admin_required
from app.extensions import db
from app.models import AppSetting
from app.settings import bp
from app.utils.constants import (
    DEFAULT_COMPACT_FIELDS,
    PERSONNEL_LIST_FIELDS,
    SETTING_COMPACT_FIELDS,
)


@bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def index():
    if request.method == "POST":
        selected = request.form.getlist("fields")
        if "full_name" not in selected:
            selected.insert(0, "full_name")
        AppSetting.set_value(SETTING_COMPACT_FIELDS, selected)
        flash("Đã lưu cấu hình hiển thị rút gọn.", "success")
        return redirect(url_for("settings.index"))

    compact_fields = AppSetting.get_value(SETTING_COMPACT_FIELDS, DEFAULT_COMPACT_FIELDS)
    return render_template(
        "settings/index.html",
        all_fields=PERSONNEL_LIST_FIELDS,
        compact_fields=compact_fields,
    )
