# -*- coding: utf-8 -*-
"""Ghi nhat ky hoat dong nguoi dung."""
from flask import has_request_context, request
from flask_login import current_user

from app.extensions import db

ACTION_LABELS = {
    "login": "Đăng nhập",
    "login_failed": "Đăng nhập thất bại",
    "logout": "Đăng xuất",
    "personnel_create": "Thêm hồ sơ",
    "personnel_update": "Sửa hồ sơ",
    "personnel_archive": "Chuyển vào Hồ sơ lưu",
    "personnel_delete": "Xóa vĩnh viễn hồ sơ",
    "personnel_restore": "Khôi phục hồ sơ",
    "personnel_import": "Nhập Excel",
    "personnel_export": "Xuất Excel",
    "user_create": "Tạo tài khoản",
    "user_update": "Sửa tài khoản",
    "user_delete": "Xóa tài khoản",
    "settings_update": "Cập nhật cấu hình",
    "data_wipe": "Xóa toàn bộ dữ liệu",
}


def log_activity(action, target=None, details=None, user=None, commit=True):
    """Ghi 1 dong nhat ky. Khong bao gio lam hong request neu ghi log loi."""
    from app.models import ActivityLog

    try:
        if user is None and current_user and current_user.is_authenticated:
            user = current_user
        ip = None
        if has_request_context():
            ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            if ip:
                ip = ip.split(",")[0].strip()[:64]
        entry = ActivityLog(
            user_id=getattr(user, "id", None),
            username=getattr(user, "username", None),
            action=action,
            target=(target or "")[:255] or None,
            details=details,
            ip_address=ip,
        )
        db.session.add(entry)
        if commit:
            db.session.commit()
    except Exception:
        db.session.rollback()
