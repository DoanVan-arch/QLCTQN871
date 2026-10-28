# -*- coding: utf-8 -*-
from flask import render_template
from flask_login import login_required

from app.main import bp
from app.models import Personnel
from app.utils.constants import (
    CATEGORY_ARCHIVE,
    CATEGORY_CADRE,
    CATEGORY_DOMESTIC,
    CATEGORY_FOREIGN,
    CATEGORY_LABELS,
    RANK_DISPLAY,
)
from app.utils.forecast import STATUS_OVERDUE, STATUS_UPCOMING, party_official_forecast, rank_forecast

# 3 danh muc "dang hoat dong" duoc dua vao bang thong ke tong hop tren Dashboard
# (khong tinh Ho so luu vi day la noi luu cac ho so da bi xoa khoi quan ly)
DASHBOARD_CATEGORIES = [
    (CATEGORY_CADRE, CATEGORY_LABELS[CATEGORY_CADRE]),
    (CATEGORY_DOMESTIC, CATEGORY_LABELS[CATEGORY_DOMESTIC]),
    (CATEGORY_FOREIGN, CATEGORY_LABELS[CATEGORY_FOREIGN]),
]


@bp.route("/")
@login_required
def dashboard():
    category_counts = {}
    for cat in (CATEGORY_DOMESTIC, CATEGORY_FOREIGN, CATEGORY_CADRE, CATEGORY_ARCHIVE):
        category_counts[cat] = Personnel.query.filter_by(category=cat).count()

    total_all = sum(category_counts.values())

    # Thong ke Dang/Doan chi tinh tren quan nhan dang tai ngu (khong tinh ho so luu)
    active_query = Personnel.query.filter(Personnel.category != CATEGORY_ARCHIVE)
    active_personnel = active_query.all()

    total_active = len(active_personnel)
    party_members = [p for p in active_personnel if p.is_party_member]
    official_party_members = [p for p in active_personnel if p.is_official_party_member]
    probationary_party_members = [p for p in active_personnel if p.is_probationary_party_member]
    youth_union_members = [p for p in active_personnel if p.is_youth_union_member]

    # Du bao / canh bao thang cap bac va chuyen Dang chinh thuc
    rank_alerts = []
    party_alerts = []
    for p in active_personnel:
        rf = rank_forecast(p.rank, p.rank_date)
        if rf["status"] in (STATUS_UPCOMING, STATUS_OVERDUE):
            rank_alerts.append((p, rf))
        pf = party_official_forecast(p.party_join_date, p.party_official_date)
        if pf["status"] in (STATUS_UPCOMING, STATUS_OVERDUE):
            party_alerts.append((p, pf))

    rank_alerts.sort(key=lambda t: (t[1]["status"] != STATUS_OVERDUE, t[1]["expected_date"] or ""))
    party_alerts.sort(key=lambda t: (t[1]["status"] != STATUS_OVERDUE, t[1]["expected_date"] or ""))

    # Phan bo theo cap bac (cho bieu do)
    rank_distribution = {}
    for p in active_personnel:
        if p.rank:
            rank_distribution[p.rank] = rank_distribution.get(p.rank, 0) + 1

    gender_distribution = {}
    for p in active_personnel:
        g = p.gender or "Chưa rõ"
        gender_distribution[g] = gender_distribution.get(g, 0) + 1

    # Bang thong ke tong hop theo tung danh muc (Quan so khung / Trong nuoc / Ngoai nuoc)
    summary_rows = [
        {"label": "Tổng số hồ sơ", "icon": "bi-people-fill"},
        {"label": "Đảng viên chính thức", "icon": "bi-patch-check-fill"},
        {"label": "Đảng viên dự bị", "icon": "bi-patch-check"},
        {"label": "Đoàn viên", "icon": "bi-flag-fill"},
        {"label": "Đã học lớp cảm tình Đảng", "icon": "bi-book-half"},
    ]
    metric_funcs = [
        lambda items: len(items),
        lambda items: sum(1 for p in items if p.is_official_party_member),
        lambda items: sum(1 for p in items if p.is_probationary_party_member),
        lambda items: sum(1 for p in items if p.is_youth_union_member),
        lambda items: sum(1 for p in items if p.party_sympathy_class),
    ]
    for row, func in zip(summary_rows, metric_funcs):
        row["values"] = {}
        row["total"] = 0
        for cat_value, _ in DASHBOARD_CATEGORIES:
            cat_items = [p for p in active_personnel if p.category == cat_value]
            count = func(cat_items)
            row["values"][cat_value] = count
            row["total"] += count

    return render_template(
        "dashboard.html",
        category_counts=category_counts,
        category_labels=CATEGORY_LABELS,
        total_all=total_all,
        total_active=total_active,
        party_members_count=len(party_members),
        official_party_count=len(official_party_members),
        probationary_party_count=len(probationary_party_members),
        youth_union_count=len(youth_union_members),
        rank_alerts=rank_alerts[:30],
        party_alerts=party_alerts[:30],
        rank_alerts_total=len(rank_alerts),
        party_alerts_total=len(party_alerts),
        rank_distribution=rank_distribution,
        gender_distribution=gender_distribution,
        rank_display=RANK_DISPLAY,
        dashboard_categories=DASHBOARD_CATEGORIES,
        summary_rows=summary_rows,
    )
