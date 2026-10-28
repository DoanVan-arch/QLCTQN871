# -*- coding: utf-8 -*-
from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.decorators import admin_required
from app.extensions import db
from app.models import AppSetting, Personnel
from app.settings import bp
from app.utils.constants import (
    DEFAULT_COMPACT_FIELDS,
    PERSONNEL_LIST_FIELDS,
    SETTING_COMPACT_FIELDS,
)
from app.utils.uploads import delete_evidence_file

CONFIRM_PHRASE = "XOA HET DU LIEU"


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
    total_personnel = Personnel.query.count()
    return render_template(
        "settings/index.html",
        all_fields=PERSONNEL_LIST_FIELDS,
        compact_fields=compact_fields,
        total_personnel=total_personnel,
        confirm_phrase=CONFIRM_PHRASE,
    )


@bp.route("/wipe-data", methods=["POST"])
@login_required
@admin_required
def wipe_data():
    confirm_text = (request.form.get("confirm_text") or "").strip()
    if confirm_text != CONFIRM_PHRASE:
        flash(f'Bạn phải nhập đúng cụm từ xác nhận "{CONFIRM_PHRASE}" để xóa toàn bộ dữ liệu.', "warning")
        return redirect(url_for("settings.index"))

    people = Personnel.query.all()
    count = len(people)
    for person in people:
        delete_evidence_file(person.reward_evidence_file)
        db.session.delete(person)
    db.session.commit()

    flash(f"Đã xóa vĩnh viễn toàn bộ {count} hồ sơ nhân sự trong hệ thống.", "success")
    return redirect(url_for("settings.index"))
