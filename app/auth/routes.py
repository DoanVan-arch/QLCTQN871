# -*- coding: utf-8 -*-
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth import bp
from app.forms import LoginForm
from app.models import User
from app.utils.activity import log_activity


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user is None or not user.check_password(form.password.data):
            log_activity("login_failed", target=form.username.data.strip()[:80], user=user)
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "danger")
        elif not user.is_active_account:
            log_activity("login_failed", target=user.username, details="Tài khoản bị khóa", user=user)
            flash("Tài khoản của bạn đã bị khóa. Vui lòng liên hệ quản trị viên.", "danger")
        else:
            login_user(user)
            log_activity("login", target=user.username, user=user)
            flash(f"Xin chào {user.full_name or user.username}!", "success")
            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("main.dashboard")
            return redirect(next_page)

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    log_activity("logout", target=current_user.username)
    logout_user()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))
