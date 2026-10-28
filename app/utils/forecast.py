# -*- coding: utf-8 -*-
"""Tinh toan, du bao thoi gian xet thang quan ham va chuyen Dang chinh thuc."""
from datetime import date

from app.utils.constants import RANK_NEXT, RANK_YEARS_TO_NEXT

STATUS_OK = "ok"            # con nhieu thoi gian
STATUS_UPCOMING = "upcoming"  # sap den han (trong khoang canh bao / trong nam nay)
STATUS_OVERDUE = "overdue"   # qua han, chua ghi nhan thang/chuyen chinh thuc
STATUS_NONE = "none"        # khong co du lieu hoac da cap bac cao nhat


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # xu ly ngay 29/2
        return d.replace(month=2, day=28, year=d.year + years)


def rank_forecast(rank, rank_date, today=None, warning_months=3):
    """Tra ve dict thong tin du bao thang quan ham tiep theo.

    Keys: next_rank, expected_date, status, years_required, months_left
    """
    today = today or date.today()
    result = {
        "next_rank": None,
        "expected_date": None,
        "status": STATUS_NONE,
        "years_required": None,
        "months_left": None,
    }
    if not rank or not rank_date:
        return result

    years = RANK_YEARS_TO_NEXT.get(rank)
    next_rank = RANK_NEXT.get(rank)
    if not years or not next_rank:
        # Da o cap cao nhat trong bang quy dinh (vd Dai ta) hoac cap khong xac dinh
        result["status"] = STATUS_NONE
        return result

    expected_date = _add_years(rank_date, years)
    result["next_rank"] = next_rank
    result["expected_date"] = expected_date
    result["years_required"] = years

    delta_months = (expected_date.year - today.year) * 12 + (expected_date.month - today.month)
    result["months_left"] = delta_months

    if expected_date <= today:
        result["status"] = STATUS_OVERDUE
    elif expected_date.year == today.year or delta_months <= warning_months:
        result["status"] = STATUS_UPCOMING
    else:
        result["status"] = STATUS_OK
    return result


def party_official_forecast(party_join_date, party_official_date, today=None, warning_months=3):
    """Du bao thoi diem chuyen Dang chinh thuc (sau 1 nam ke tu ngay vao Dang du bi).

    Neu da co ngay chinh thuc -> coi nhu da hoan tat, tra ve status NONE.
    """
    today = today or date.today()
    result = {
        "expected_date": None,
        "status": STATUS_NONE,
        "months_left": None,
    }
    if party_official_date:
        return result
    if not party_join_date:
        return result

    expected_date = _add_years(party_join_date, 1)
    result["expected_date"] = expected_date

    delta_months = (expected_date.year - today.year) * 12 + (expected_date.month - today.month)
    result["months_left"] = delta_months

    if expected_date <= today:
        result["status"] = STATUS_OVERDUE
    elif expected_date.year == today.year or delta_months <= warning_months:
        result["status"] = STATUS_UPCOMING
    else:
        result["status"] = STATUS_OK
    return result


def graduation_forecast(graduation_date, today=None, warning_months=3):
    """Du bao hoc vien sap/da den ngay ra truong (tot nghiep).

    - upcoming: ngay tot nghiep nam trong khoang canh bao (sap toi).
    - overdue: ngay tot nghiep da qua nhung ho so van con trong danh muc dang quan ly
      (can cap nhat trang thai/ra truong).
    """
    today = today or date.today()
    result = {
        "expected_date": graduation_date,
        "status": STATUS_NONE,
        "months_left": None,
    }
    if not graduation_date:
        return result

    delta_months = (graduation_date.year - today.year) * 12 + (graduation_date.month - today.month)
    result["months_left"] = delta_months

    if graduation_date < today:
        result["status"] = STATUS_OVERDUE
    elif delta_months <= warning_months:
        result["status"] = STATUS_UPCOMING
    else:
        result["status"] = STATUS_OK
    return result
