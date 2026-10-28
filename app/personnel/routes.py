# -*- coding: utf-8 -*-
import io
from datetime import date, datetime

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.decorators import edit_required
from app.extensions import db
from app.forms import PersonnelForm
from app.models import AppSetting, Personnel
from app.personnel import bp
from app.utils.constants import (
    CATEGORY_ARCHIVE,
    CATEGORY_LABELS,
    CATEGORY_SINGULAR,
    DEFAULT_COMPACT_FIELDS,
    EDUCATION_LEVEL_CHOICES,
    GENDER_CHOICES,
    PERSONNEL_LIST_FIELDS,
    RANK_CHOICES,
    SETTING_COMPACT_FIELDS,
)
from app.utils.excel import build_import_template, export_personnel_to_excel, parse_personnel_excel
from app.utils.forecast import party_official_forecast, rank_forecast
from app.utils.uploads import delete_evidence_file, save_evidence_file

VALID_CATEGORIES = set(CATEGORY_LABELS.keys())

SORTABLE_COLUMNS = {
    "full_name": Personnel.full_name,
    "gender": Personnel.gender,
    "date_of_birth": Personnel.date_of_birth,
    "enlistment_date": Personnel.enlistment_date,
    "rank": Personnel.rank,
    "rank_date": Personnel.rank_date,
    "position": Personnel.position,
    "position_date": Personnel.position_date,
    "youth_union_date": Personnel.youth_union_date,
    "party_join_date": Personnel.party_join_date,
    "party_official_date": Personnel.party_official_date,
    "school_name": Personnel.school_name,
    "graduation_date": Personnel.graduation_date,
    "ethnicity": Personnel.ethnicity,
    "religion": Personnel.religion,
    "created_at": Personnel.created_at,
}


@bp.url_value_preprocessor
def pull_category(endpoint, values):
    category = values.get("category") if values else None
    if category not in VALID_CATEGORIES:
        abort(404)


@bp.route("/")
@login_required
def index(category):
    q = request.args.get("q", "").strip()
    rank_filter = request.args.get("rank", "")
    gender_filter = request.args.get("gender", "")
    education_filter = request.args.get("education_level", "")
    party_filter = request.args.get("party_status", "")  # '', 'official', 'probationary', 'none'
    sort_by = request.args.get("sort_by", "full_name")
    sort_dir = request.args.get("sort_dir", "asc")
    page = request.args.get("page", 1, type=int)

    view_mode = request.args.get("view")
    session_key = f"view_mode_{category}"
    if view_mode in ("full", "compact"):
        session[session_key] = view_mode
    else:
        view_mode = session.get(session_key, "full")

    compact_fields = AppSetting.get_value(SETTING_COMPACT_FIELDS, DEFAULT_COMPACT_FIELDS)
    if view_mode == "full":
        visible_fields = PERSONNEL_LIST_FIELDS
    else:
        visible_fields = [f for f in PERSONNEL_LIST_FIELDS if f[0] in compact_fields]

    query = Personnel.query.filter_by(category=category)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Personnel.full_name.ilike(like),
                Personnel.phone.ilike(like),
                Personnel.citizen_id.ilike(like),
                Personnel.officer_id.ilike(like),
                Personnel.hometown.ilike(like),
                Personnel.position.ilike(like),
                Personnel.school_name.ilike(like),
                Personnel.unit_before_enrollment.ilike(like),
                Personnel.current_residence.ilike(like),
            )
        )

    if rank_filter:
        query = query.filter(Personnel.rank == rank_filter)
    if gender_filter:
        query = query.filter(Personnel.gender == gender_filter)
    if education_filter:
        query = query.filter(Personnel.education_level == education_filter)
    if party_filter == "official":
        query = query.filter(Personnel.party_official_date.isnot(None))
    elif party_filter == "probationary":
        query = query.filter(
            Personnel.party_join_date.isnot(None), Personnel.party_official_date.is_(None)
        )
    elif party_filter == "none":
        query = query.filter(Personnel.party_join_date.is_(None))

    sort_col = SORTABLE_COLUMNS.get(sort_by, Personnel.full_name)
    if sort_dir == "desc":
        sort_col = sort_col.desc()
    else:
        sort_col = sort_col.asc()
    query = query.order_by(sort_col)

    pagination = query.paginate(page=page, per_page=20, error_out=False)
    items = pagination.items

    today = date.today()
    forecasts = {}
    for p in items:
        rf = rank_forecast(p.rank, p.rank_date, today=today)
        pf = party_official_forecast(p.party_join_date, p.party_official_date, today=today)
        forecasts[p.id] = {"rank": rf, "party": pf}

    return render_template(
        "personnel/list.html",
        category=category,
        category_label=CATEGORY_LABELS[category],
        category_singular=CATEGORY_SINGULAR[category],
        items=items,
        pagination=pagination,
        forecasts=forecasts,
        q=q,
        rank_filter=rank_filter,
        gender_filter=gender_filter,
        education_filter=education_filter,
        party_filter=party_filter,
        sort_by=sort_by,
        sort_dir=sort_dir,
        rank_choices=RANK_CHOICES,
        gender_choices=GENDER_CHOICES,
        education_choices=EDUCATION_LEVEL_CHOICES,
        view_mode=view_mode,
        all_fields=PERSONNEL_LIST_FIELDS,
        visible_fields=visible_fields,
        compact_fields=compact_fields,
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
@edit_required
def create(category):
    form = PersonnelForm(category=category)
    form.category.data = category
    if form.validate_on_submit():
        person = Personnel(category=category)
        form.populate_obj(person)
        person.category = category  # dam bao khong bi doi boi form
        person.party_sympathy_class = form.party_sympathy_class.data == "Có"
        person.reward_evidence_file = save_evidence_file(form.reward_evidence.data)
        person.created_by = current_user.id
        person.updated_by = current_user.id
        db.session.add(person)
        db.session.commit()
        flash("Đã thêm hồ sơ mới thành công.", "success")
        return redirect(url_for("personnel.index", category=category))
    return render_template(
        "personnel/form.html",
        form=form,
        category=category,
        category_label=CATEGORY_LABELS[category],
        is_new=True,
    )


@bp.route("/<int:person_id>")
@login_required
def view(category, person_id):
    person = Personnel.query.filter_by(category=category, id=person_id).first_or_404()
    rf = rank_forecast(person.rank, person.rank_date)
    pf = party_official_forecast(person.party_join_date, person.party_official_date)
    return render_template(
        "personnel/view.html",
        person=person,
        category=category,
        category_label=CATEGORY_LABELS[category],
        rank_forecast_info=rf,
        party_forecast_info=pf,
    )


@bp.route("/<int:person_id>/edit", methods=["GET", "POST"])
@login_required
@edit_required
def edit(category, person_id):
    person = Personnel.query.filter_by(category=category, id=person_id).first_or_404()
    form = PersonnelForm(obj=person)
    if form.validate_on_submit():
        form.populate_obj(person)
        person.category = category
        person.party_sympathy_class = form.party_sympathy_class.data == "Có"

        if form.remove_reward_evidence.data and person.reward_evidence_file:
            delete_evidence_file(person.reward_evidence_file)
            person.reward_evidence_file = None

        new_file = save_evidence_file(form.reward_evidence.data)
        if new_file:
            delete_evidence_file(person.reward_evidence_file)
            person.reward_evidence_file = new_file

        person.updated_by = current_user.id
        db.session.commit()
        flash("Đã cập nhật hồ sơ.", "success")
        return redirect(url_for("personnel.view", category=category, person_id=person.id))

    if request.method == "GET":
        form.party_sympathy_class.data = "Có" if person.party_sympathy_class else "Không"

    return render_template(
        "personnel/form.html",
        form=form,
        category=category,
        category_label=CATEGORY_LABELS[category],
        is_new=False,
        person=person,
    )


@bp.route("/<int:person_id>/delete", methods=["POST"])
@login_required
@edit_required
def delete(category, person_id):
    person = Personnel.query.filter_by(category=category, id=person_id).first_or_404()

    if category == CATEGORY_ARCHIVE:
        # Da nam trong Ho so luu -> xoa vinh vien that su
        delete_evidence_file(person.reward_evidence_file)
        db.session.delete(person)
        db.session.commit()
        flash("Đã xóa vĩnh viễn hồ sơ khỏi Hồ sơ lưu.", "success")
        return redirect(url_for("personnel.index", category=category))

    # Chuyen hoso sang muc "Ho so luu" thay vi xoa that
    person.archived_from_category = category
    person.archived_at = datetime.utcnow()
    person.category = CATEGORY_ARCHIVE
    person.updated_by = current_user.id
    db.session.commit()
    flash("Đã chuyển hồ sơ vào mục Hồ sơ lưu.", "success")
    return redirect(url_for("personnel.index", category=category))


@bp.route("/<int:person_id>/restore", methods=["POST"])
@login_required
@edit_required
def restore(category, person_id):
    if category != CATEGORY_ARCHIVE:
        abort(404)
    person = Personnel.query.filter_by(category=category, id=person_id).first_or_404()
    target_category = person.archived_from_category or "trong_nuoc"
    person.category = target_category
    person.archived_from_category = None
    person.archived_at = None
    person.updated_by = current_user.id
    db.session.commit()
    flash("Đã khôi phục hồ sơ.", "success")
    return redirect(url_for("personnel.index", category=category))


@bp.route("/bulk-delete", methods=["POST"])
@login_required
@edit_required
def bulk_delete(category):
    ids = request.form.getlist("ids", type=int)
    if not ids:
        flash("Vui lòng chọn ít nhất một hồ sơ để xóa.", "warning")
        return redirect(url_for("personnel.index", category=category))

    people = Personnel.query.filter(Personnel.category == category, Personnel.id.in_(ids)).all()

    if category == CATEGORY_ARCHIVE:
        for person in people:
            delete_evidence_file(person.reward_evidence_file)
            db.session.delete(person)
        db.session.commit()
        flash(f"Đã xóa vĩnh viễn {len(people)} hồ sơ khỏi Hồ sơ lưu.", "success")
        return redirect(url_for("personnel.index", category=category))

    for person in people:
        person.archived_from_category = category
        person.archived_at = datetime.utcnow()
        person.category = CATEGORY_ARCHIVE
        person.updated_by = current_user.id
    db.session.commit()
    flash(f"Đã chuyển {len(people)} hồ sơ vào mục Hồ sơ lưu.", "success")
    return redirect(url_for("personnel.index", category=category))


@bp.route("/export")
@login_required
def export_excel(category):
    q = request.args.get("q", "").strip()
    rank_filter = request.args.get("rank", "")
    gender_filter = request.args.get("gender", "")
    education_filter = request.args.get("education_level", "")
    party_filter = request.args.get("party_status", "")

    query = Personnel.query.filter_by(category=category)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Personnel.full_name.ilike(like),
                Personnel.phone.ilike(like),
                Personnel.citizen_id.ilike(like),
                Personnel.officer_id.ilike(like),
                Personnel.hometown.ilike(like),
                Personnel.position.ilike(like),
                Personnel.school_name.ilike(like),
            )
        )
    if rank_filter:
        query = query.filter(Personnel.rank == rank_filter)
    if gender_filter:
        query = query.filter(Personnel.gender == gender_filter)
    if education_filter:
        query = query.filter(Personnel.education_level == education_filter)
    if party_filter == "official":
        query = query.filter(Personnel.party_official_date.isnot(None))
    elif party_filter == "probationary":
        query = query.filter(
            Personnel.party_join_date.isnot(None), Personnel.party_official_date.is_(None)
        )
    elif party_filter == "none":
        query = query.filter(Personnel.party_join_date.is_(None))

    items = query.order_by(Personnel.full_name.asc()).all()
    wb = export_personnel_to_excel(items)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"{category}_{date.today().isoformat()}.xlsx"
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/import-template")
@login_required
@edit_required
def import_template(category):
    wb = build_import_template()
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"mau_nhap_{category}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/import", methods=["GET", "POST"])
@login_required
@edit_required
def import_excel(category):
    if request.method == "POST":
        upload = request.files.get("excel_file")
        if not upload or upload.filename == "":
            flash("Vui lòng chọn file Excel (.xlsx) để nhập.", "warning")
            return redirect(url_for("personnel.import_excel", category=category))

        try:
            rows, errors = parse_personnel_excel(upload)
        except Exception:
            flash("File không đúng định dạng. Vui lòng dùng file mẫu được cung cấp.", "danger")
            return redirect(url_for("personnel.import_excel", category=category))

        created_count = 0
        for data in rows:
            person = Personnel(category=category)
            for field, value in data.items():
                setattr(person, field, value)
            person.created_by = current_user.id
            person.updated_by = current_user.id
            db.session.add(person)
            created_count += 1
        db.session.commit()

        flash(f"Đã nhập thành công {created_count} hồ sơ.", "success")
        for err in errors[:20]:
            flash(err, "warning")
        return redirect(url_for("personnel.index", category=category))

    return render_template(
        "personnel/import.html",
        category=category,
        category_label=CATEGORY_LABELS[category],
    )
