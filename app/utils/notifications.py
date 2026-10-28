# -*- coding: utf-8 -*-
"""Tong hop cac canh bao (thang quan ham, chuyen Dang chinh thuc, sap ra truong)
dung chung cho chuong thong bao (bell) va trang Thong ke."""
from datetime import date

from app.models import Personnel
from app.utils.constants import CATEGORY_ARCHIVE, CATEGORY_DOMESTIC, CATEGORY_FOREIGN
from app.utils.forecast import (
    STATUS_OVERDUE,
    STATUS_UPCOMING,
    graduation_forecast,
    party_official_forecast,
    rank_forecast,
)


def collect_alerts(today=None):
    """Quet toan bo nhan su dang quan ly (khong tinh Ho so luu) va tra ve danh sach
    canh bao da duoc phan loai + sap xep (qua han truoc, sap den han sau)."""
    today = today or date.today()
    active_items = Personnel.query.filter(Personnel.category != CATEGORY_ARCHIVE).all()
    study_categories = (CATEGORY_DOMESTIC, CATEGORY_FOREIGN)

    rank_alerts = []
    party_alerts = []
    graduation_alerts = []

    for p in active_items:
        rf = rank_forecast(p.rank, p.rank_date, today=today)
        if rf["status"] in (STATUS_UPCOMING, STATUS_OVERDUE):
            rank_alerts.append({"person": p, "forecast": rf, "type": "rank"})

        pf = party_official_forecast(p.party_join_date, p.party_official_date, today=today)
        if pf["status"] in (STATUS_UPCOMING, STATUS_OVERDUE):
            party_alerts.append({"person": p, "forecast": pf, "type": "party"})

        if p.category in study_categories:
            gf = graduation_forecast(p.graduation_date, today=today)
            if gf["status"] in (STATUS_UPCOMING, STATUS_OVERDUE):
                graduation_alerts.append({"person": p, "forecast": gf, "type": "graduation"})

    def _sort_key(item):
        return (item["forecast"]["status"] != STATUS_OVERDUE, item["forecast"]["expected_date"] or date.max)

    rank_alerts.sort(key=_sort_key)
    party_alerts.sort(key=_sort_key)
    graduation_alerts.sort(key=_sort_key)

    return {
        "rank_alerts": rank_alerts,
        "party_alerts": party_alerts,
        "graduation_alerts": graduation_alerts,
        "rank_total": len(rank_alerts),
        "party_total": len(party_alerts),
        "graduation_total": len(graduation_alerts),
        "total": len(rank_alerts) + len(party_alerts) + len(graduation_alerts),
    }


def notification_feed(limit=8):
    """Tra ve danh sach rut gon (moi nguoi 1 dong canh bao quan trong nhat) de hien
    thi trong chuong thong bao, uu tien qua han truoc."""
    data = collect_alerts()
    combined = data["rank_alerts"] + data["party_alerts"] + data["graduation_alerts"]
    combined.sort(key=lambda item: (item["forecast"]["status"] != STATUS_OVERDUE, item["forecast"]["expected_date"] or date.max))

    labels = {
        "rank": "Sắp/Quá hạn thăng quân hàm",
        "party": "Sắp/Quá hạn chuyển Đảng chính thức",
        "graduation": "Sắp/Đã đến ngày ra trường",
    }
    icons = {
        "rank": "bi-stars",
        "party": "bi-flag-fill",
        "graduation": "bi-mortarboard-fill",
    }

    feed = []
    for item in combined[:limit]:
        feed.append(
            {
                "person": item["person"],
                "type_label": labels[item["type"]],
                "icon": icons[item["type"]],
                "status": item["forecast"]["status"],
                "expected_date": item["forecast"]["expected_date"],
            }
        )

    return {"entries": feed, "total": data["total"]}
