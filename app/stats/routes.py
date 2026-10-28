# -*- coding: utf-8 -*-
import re
from datetime import date

from flask import render_template, request
from flask_login import login_required
from sqlalchemy import or_

from app.models import Personnel
from app.stats import bp
from app.utils.constants import (
    CATEGORY_CHOICES,
    CATEGORY_LABELS,
    EDUCATION_LEVEL_CHOICES,
    GENDER_CHOICES,
    RANK_CHOICES,
)
from app.utils.forecast import (
    STATUS_NONE,
    STATUS_OK,
    STATUS_OVERDUE,
    STATUS_UPCOMING,
    party_official_forecast,
    rank_forecast,
)
from app.utils.notifications import collect_alerts

PER_PAGE = 20

RANK_STATUS_LABELS = {
    STATUS_OK: "Còn thời gian",
    STATUS_UPCOMING: "Sắp đến hạn",
    STATUS_OVERDUE: "Quá hạn",
    STATUS_NONE: "Không áp dụng",
}


def _build_breakdown(items, attr, label_default="Chưa cập nhật"):
    counts = {}
    for p in items:
        value = getattr(p, attr) or label_default
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


_PROVINCE_PREFIX_RE = re.compile(r"^(tỉnh|thành phố|tp\.?)\s*", re.IGNORECASE)


def _extract_province(address):
    """Lay phan tinh/thanh pho tu chuoi dia chi (que quan hoac noi o), vd:
    'Xã A, Huyện B, Tỉnh Nam Định' -> 'Nam Định'. Tu dong bo tien to
    'Tỉnh'/'Thành phố'/'TP' o dau neu co (khong phan biet hoa/thuong)."""
    if not address:
        return None
    parts = [p.strip() for p in address.split(",") if p.strip()]
    province = parts[-1] if parts else address.strip()
    province = _PROVINCE_PREFIX_RE.sub("", province).strip()
    return province or None


def _build_province_breakdown(items, attr="hometown", label_default="Chưa cập nhật"):
    counts = {}
    for p in items:
        province = _extract_province(getattr(p, attr, None)) or label_default
        counts[province] = counts.get(province, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


@bp.route("/")
@login_required
def index():
    all_items = Personnel.query.all()

    # --- Cac bang thong ke tong hop ---
    by_category = {}
    for value, label in CATEGORY_CHOICES:
        by_category[label] = sum(1 for p in all_items if p.category == value)

    by_rank = _build_breakdown(all_items, "rank")
    by_gender = _build_breakdown(all_items, "gender")
    by_ethnicity = _build_breakdown(all_items, "ethnicity")
    by_education = _build_breakdown(all_items, "education_level")
    by_school = _build_breakdown(all_items, "school_name")
    by_hometown = _build_province_breakdown(all_items, attr="hometown")
    by_residence = _build_province_breakdown(all_items, attr="current_residence")
    by_major = _build_breakdown(all_items, "major")

    party_official = sum(1 for p in all_items if p.is_official_party_member)
    party_probationary = sum(1 for p in all_items if p.is_probationary_party_member)
    youth_union = sum(1 for p in all_items if p.is_youth_union_member)
    sympathy_class = sum(1 for p in all_items if p.party_sympathy_class)

    # Bang cheo: Danh muc x Bac hoc
    category_education_matrix = []
    for value, label in CATEGORY_CHOICES:
        cat_items = [p for p in all_items if p.category == value]
        row = {"label": label, "total": len(cat_items)}
        for level in EDUCATION_LEVEL_CHOICES:
            row[level] = sum(1 for p in cat_items if p.education_level == level)
        category_education_matrix.append(row)

    # Top truong hoc nhieu hoc vien nhat
    top_schools = list(by_school.items())[:15]
    # Top tinh/thanh (que quan, noi o) va chuyen nganh nhieu nguoi nhat
    top_hometowns = list(by_hometown.items())[:15]
    top_residences = list(by_residence.items())[:15]
    top_majors = list(by_major.items())[:15]

    # --- Canh bao tong hop: thang quan ham / chuyen Dang chinh thuc / sap ra truong ---
    alerts = collect_alerts(today=date.today())

    # --- Bang tim kiem / sap xep chi tiet toan bo nhan su ---
    q = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "")
    rank_filter = request.args.get("rank", "")
    gender_filter = request.args.get("gender", "")
    rank_status_filter = request.args.get("rank_status", "")
    party_status_filter = request.args.get("party_status", "")
    sort_by = request.args.get("sort_by", "full_name")
    sort_dir = request.args.get("sort_dir", "asc")
    page = request.args.get("page", 1, type=int)

    query = Personnel.query
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
    if category_filter:
        query = query.filter(Personnel.category == category_filter)
    if rank_filter:
        query = query.filter(Personnel.rank == rank_filter)
    if gender_filter:
        query = query.filter(Personnel.gender == gender_filter)

    filtered_items = query.all()

    today = date.today()
    rows = []
    for p in filtered_items:
        rf = rank_forecast(p.rank, p.rank_date, today=today)
        pf = party_official_forecast(p.party_join_date, p.party_official_date, today=today)
        rows.append({"person": p, "rank_forecast": rf, "party_forecast": pf})

    if rank_status_filter:
        rows = [r for r in rows if r["rank_forecast"]["status"] == rank_status_filter]
    if party_status_filter:
        rows = [r for r in rows if r["party_forecast"]["status"] == party_status_filter]

    simple_fields = {
        "full_name": lambda r: (r["person"].full_name or "").lower(),
        "category": lambda r: CATEGORY_LABELS.get(r["person"].category, ""),
        "rank": lambda r: r["person"].rank or "",
        "gender": lambda r: r["person"].gender or "",
        "date_of_birth": lambda r: r["person"].date_of_birth or date.min,
        "rank_date": lambda r: r["person"].rank_date or date.min,
        "party_join_date": lambda r: r["person"].party_join_date or date.min,
        "rank_expected_date": lambda r: r["rank_forecast"]["expected_date"] or date.max,
        "party_expected_date": lambda r: r["party_forecast"]["expected_date"] or date.max,
    }
    key_func = simple_fields.get(sort_by, simple_fields["full_name"])
    rows.sort(key=key_func, reverse=(sort_dir == "desc"))

    total_rows = len(rows)
    total_pages = max(1, (total_rows + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PER_PAGE
    page_rows = rows[start : start + PER_PAGE]

    return render_template(
        "stats/index.html",
        by_category=by_category,
        by_rank=by_rank,
        by_gender=by_gender,
        by_ethnicity=by_ethnicity,
        by_education=by_education,
        by_school=by_school,
        top_schools=top_schools,
        by_hometown=by_hometown,
        top_hometowns=top_hometowns,
        by_residence=by_residence,
        top_residences=top_residences,
        by_major=by_major,
        top_majors=top_majors,
        category_education_matrix=category_education_matrix,
        education_level_choices=EDUCATION_LEVEL_CHOICES,
        party_official=party_official,
        party_probationary=party_probationary,
        youth_union=youth_union,
        sympathy_class=sympathy_class,
        total_all=len(all_items),
        rows=page_rows,
        total_rows=total_rows,
        page=page,
        total_pages=total_pages,
        q=q,
        category_filter=category_filter,
        rank_filter=rank_filter,
        gender_filter=gender_filter,
        rank_status_filter=rank_status_filter,
        party_status_filter=party_status_filter,
        sort_by=sort_by,
        sort_dir=sort_dir,
        category_choices=CATEGORY_CHOICES,
        rank_choices=RANK_CHOICES,
        gender_choices=GENDER_CHOICES,
        education_choices=EDUCATION_LEVEL_CHOICES,
        rank_status_labels=RANK_STATUS_LABELS,
        category_labels=CATEGORY_LABELS,
        alerts=alerts,
    )
