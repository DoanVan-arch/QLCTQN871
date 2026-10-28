# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DateField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, Optional, EqualTo

from app.utils.constants import (
    CATEGORY_CHOICES,
    EDUCATION_LEVEL_CHOICES,
    GENDER_CHOICES,
    PARTY_SYMPATHY_CHOICES,
    RANK_CHOICES,
    ROLE_CHOICES,
)


class LoginForm(FlaskForm):
    username = StringField("Tên đăng nhập", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Mật khẩu", validators=[DataRequired()])
    submit = SubmitField("Đăng nhập")


class UserForm(FlaskForm):
    username = StringField("Tên đăng nhập", validators=[DataRequired(), Length(max=80)])
    full_name = StringField("Họ và tên", validators=[Optional(), Length(max=150)])
    role = SelectField("Vai trò", choices=ROLE_CHOICES, validators=[DataRequired()])
    password = PasswordField(
        "Mật khẩu",
        validators=[Optional(), Length(min=4, message="Mật khẩu tối thiểu 4 ký tự")],
    )
    confirm_password = PasswordField(
        "Nhập lại mật khẩu",
        validators=[Optional(), EqualTo("password", message="Mật khẩu nhập lại không khớp")],
    )
    is_active_account = BooleanField("Tài khoản đang hoạt động", default=True)
    submit = SubmitField("Lưu tài khoản")


class PersonnelForm(FlaskForm):
    category = SelectField("Danh mục quản lý", choices=CATEGORY_CHOICES, validators=[DataRequired()])

    # Thong tin ca nhan
    full_name = StringField("Họ và tên", validators=[DataRequired(), Length(max=150)])
    religion = StringField("Tôn giáo", validators=[Optional(), Length(max=100)])
    ethnicity = StringField("Dân tộc", validators=[Optional(), Length(max=100)])
    gender = SelectField("Giới tính", choices=[("", "-- Chọn --")] + [(g, g) for g in GENDER_CHOICES], validators=[Optional()])
    date_of_birth = DateField("Ngày sinh", validators=[Optional()], format="%Y-%m-%d")
    enlistment_date = DateField("Ngày nhập ngũ", validators=[Optional()], format="%Y-%m-%d")

    # Cap bac / chuc vu
    rank = SelectField("Cấp bậc", choices=[("", "-- Chọn --")] + [(r, r) for r in RANK_CHOICES], validators=[Optional()])
    rank_date = DateField("TG nhận cấp bậc", validators=[Optional()], format="%Y-%m-%d")
    position = StringField("Chức vụ", validators=[Optional(), Length(max=150)])
    position_date = DateField("TG nhận chức vụ", validators=[Optional()], format="%Y-%m-%d")

    # Doan / Dang
    youth_union_date = DateField("TG vào Đoàn", validators=[Optional()], format="%Y-%m-%d")
    youth_union_cell = StringField("Chi đoàn", validators=[Optional(), Length(max=150)])
    party_sympathy_class = SelectField(
        "Đã học lớp cảm tình Đảng",
        choices=[(c, c) for c in PARTY_SYMPATHY_CHOICES],
        validators=[Optional()],
    )
    party_join_date = DateField("TG vào Đảng (dự bị)", validators=[Optional()], format="%Y-%m-%d")
    party_cell = StringField("Chi bộ", validators=[Optional(), Length(max=150)])
    party_official_date = DateField("TG chính thức", validators=[Optional()], format="%Y-%m-%d")

    # Noi o / que quan
    unit_before_enrollment = StringField("Đơn vị trước khi nhập học", validators=[Optional(), Length(max=200)])
    current_residence = StringField("Nơi ở", validators=[Optional(), Length(max=255)])
    registered_residence = StringField("Trú quán", validators=[Optional(), Length(max=255)])
    hometown = StringField("Quê quán", validators=[Optional(), Length(max=255)])

    # Hoc tap
    school_name = StringField("Tên trường theo học", validators=[Optional(), Length(max=200)])
    major = StringField("Chuyên ngành", validators=[Optional(), Length(max=200)])
    education_level = SelectField(
        "Bậc học",
        choices=[("", "-- Chọn --")] + [(e, e) for e in EDUCATION_LEVEL_CHOICES],
        validators=[Optional()],
    )
    enrollment_date = DateField("TG nhập học", validators=[Optional()], format="%Y-%m-%d")
    reception_date = DateField("TG tiếp nhận", validators=[Optional()], format="%Y-%m-%d")
    graduation_date = DateField("TG tốt nghiệp", validators=[Optional()], format="%Y-%m-%d")

    # Khac
    rewards = TextAreaField("Khen thưởng", validators=[Optional()])
    reward_evidence = FileField(
        "File minh chứng khen thưởng (ảnh hoặc PDF)",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "gif", "pdf"], "Chỉ chấp nhận ảnh hoặc PDF")],
    )
    remove_reward_evidence = BooleanField("Xóa file minh chứng hiện tại")
    discipline = TextAreaField("Kỷ luật", validators=[Optional()])
    citizen_id = StringField("Số CCCD", validators=[Optional(), Length(max=20)])
    officer_id = StringField("CMSQ", validators=[Optional(), Length(max=20)])
    phone = StringField("Số điện thoại", validators=[Optional(), Length(max=20)])
    contact_person = StringField("Người báo tin", validators=[Optional(), Length(max=200)])
    notes = TextAreaField("Ghi chú", validators=[Optional()])

    submit = SubmitField("Lưu hồ sơ")
