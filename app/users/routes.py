# -*- coding: utf-8 -*-
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.decorators import admin_required
from app.extensions import db
from app.forms import UserForm
from app.models import User
from app.users import bp


@bp.route("/")
@login_required
@admin_required
def index():
    users = User.query.order_by(User.username).all()
    return render_template("users/list.html", users=users)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("Tên đăng nhập đã tồn tại.", "danger")
        elif not form.password.data:
            flash("Vui lòng nhập mật khẩu cho tài khoản mới.", "danger")
        else:
            user = User(
                username=form.username.data.strip(),
                full_name=form.full_name.data.strip() if form.full_name.data else "",
                role=form.role.data,
                is_active_account=form.is_active_account.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Đã tạo tài khoản mới thành công.", "success")
            return redirect(url_for("users.index"))
    return render_template("users/form.html", form=form, is_new=True)


@bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data.strip()).first()
        if existing and existing.id != user.id:
            flash("Tên đăng nhập đã tồn tại.", "danger")
        else:
            user.username = form.username.data.strip()
            user.full_name = form.full_name.data.strip() if form.full_name.data else ""
            user.role = form.role.data
            user.is_active_account = form.is_active_account.data
            if form.password.data:
                user.set_password(form.password.data)
            db.session.commit()
            flash("Đã cập nhật tài khoản.", "success")
            return redirect(url_for("users.index"))
    return render_template("users/form.html", form=form, is_new=False, user=user)


@bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Bạn không thể tự xóa chính tài khoản đang đăng nhập.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("Đã xóa tài khoản.", "success")
    return redirect(url_for("users.index"))
