# -*- coding: utf-8 -*-
from functools import wraps

from flask import abort
from flask_login import current_user


def roles_required(*roles):
    """Chi cho phep truy cap neu current_user.role nam trong danh sach roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def edit_required(view_func):
    """Chi Admin va Mod duoc phep thuc hien hanh dong them/sua/xoa."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.can_edit:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def admin_required(view_func):
    """Chi Admin duoc phep quan ly tai khoan."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped
