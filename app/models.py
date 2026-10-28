# -*- coding: utf-8 -*-
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.utils.constants import ROLE_ADMIN, ROLE_MOD, ROLE_VIEWER


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(150), nullable=False, default="")
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_VIEWER)
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.is_active_account

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_mod(self):
        return self.role == ROLE_MOD

    @property
    def is_viewer(self):
        return self.role == ROLE_VIEWER

    @property
    def can_edit(self):
        """Admin va Mod co quyen chinh sua du lieu nhan su."""
        return self.role in (ROLE_ADMIN, ROLE_MOD)

    @property
    def can_manage_users(self):
        """Chi Admin moi duoc quan ly tai khoan."""
        return self.role == ROLE_ADMIN

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class AppSetting(db.Model):
    """Bang luu cau hinh chung cua he thong (vd: danh sach truong hien thi che do rut gon)."""

    __tablename__ = "app_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)  # luu JSON

    @staticmethod
    def get_value(key, default=None):
        row = AppSetting.query.filter_by(key=key).first()
        if row is None:
            return default
        import json

        try:
            return json.loads(row.value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def set_value(key, value):
        import json

        row = AppSetting.query.filter_by(key=key).first()
        payload = json.dumps(value, ensure_ascii=False)
        if row is None:
            row = AppSetting(key=key, value=payload)
            db.session.add(row)
        else:
            row.value = payload
        db.session.commit()


class Personnel(db.Model):
    __tablename__ = "personnel"

    id = db.Column(db.Integer, primary_key=True)
    # Danh muc quan ly: trong_nuoc / ngoai_nuoc / quan_so_khung / ho_so_luu
    category = db.Column(db.String(30), nullable=False, index=True)

    # --- Thong tin ca nhan ---
    full_name = db.Column(db.String(150), nullable=False, index=True)
    religion = db.Column(db.String(100))
    ethnicity = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    enlistment_date = db.Column(db.Date)  # Ngay nhap ngu

    # --- Cap bac / chuc vu ---
    rank = db.Column(db.String(50), index=True)
    rank_date = db.Column(db.Date)  # TG nhan cap bac
    position = db.Column(db.String(150))
    position_date = db.Column(db.Date)  # TG nhan chuc vu

    # --- Doan / Dang ---
    youth_union_date = db.Column(db.Date)  # TG vao doan
    youth_union_cell = db.Column(db.String(150))  # Chi doan
    party_sympathy_class = db.Column(db.Boolean, default=False)  # Da hoc lop cam tinh dang
    party_join_date = db.Column(db.Date)  # TG vao Dang (du bi)
    party_cell = db.Column(db.String(150))  # Chi bo
    party_official_date = db.Column(db.Date)  # TG chinh thuc

    # --- Noi o / que quan ---
    unit_before_enrollment = db.Column(db.String(200))  # Don vi truoc khi nhap hoc
    current_residence = db.Column(db.String(255))  # Noi o
    registered_residence = db.Column(db.String(255))  # Tru quan
    hometown = db.Column(db.String(255))  # Que quan

    # --- Hoc tap ---
    school_name = db.Column(db.String(200))  # Ten truong theo hoc
    major = db.Column(db.String(200))  # Chuyen nganh
    education_level = db.Column(db.String(100))  # Bac hoc
    enrollment_date = db.Column(db.Date)  # TG nhap hoc
    reception_date = db.Column(db.Date)  # TG tiep nhan
    graduation_date = db.Column(db.Date)  # TG tot nghiep

    # --- Khac ---
    rewards = db.Column(db.Text)  # Khen thuong
    reward_evidence_file = db.Column(db.String(255))  # File minh chung khen thuong (anh/pdf)
    discipline = db.Column(db.Text)  # Ky luat
    citizen_id = db.Column(db.String(20))  # So CCCD
    officer_id = db.Column(db.String(20))  # CMSQ
    phone = db.Column(db.String(20))  # SDT
    contact_person = db.Column(db.String(200))  # Nguoi bao tin

    notes = db.Column(db.Text)

    # --- Luu tru khi xoa (chuyen vao Ho so luu thay vi xoa vinh vien) ---
    archived_from_category = db.Column(db.String(30))  # Danh muc goc truoc khi bi xoa/luu
    archived_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    updated_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    @property
    def is_party_member(self):
        return bool(self.party_join_date)

    @property
    def is_official_party_member(self):
        return bool(self.party_official_date)

    @property
    def is_probationary_party_member(self):
        return bool(self.party_join_date) and not bool(self.party_official_date)

    @property
    def is_youth_union_member(self):
        return bool(self.youth_union_date)

    @property
    def is_archived(self):
        from app.utils.constants import CATEGORY_ARCHIVE

        return self.category == CATEGORY_ARCHIVE

    def __repr__(self):
        return f"<Personnel {self.full_name}>"
