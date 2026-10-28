# -*- coding: utf-8 -*-
"""Cac hang so dung chung: danh sach cap bac, danh muc quan ly, vai tro..."""

# Thu tu cap bac si quan va so nam toi thieu de xet thang cap tiep theo
# (ap dung theo Luat Si quan QDND Viet Nam va yeu cau nghiep vu cua don vi)
RANK_ORDER = [
    "Thieu uy",
    "Trung uy",
    "Thuong uy",
    "Dai uy",
    "Thieu ta",
    "Trung ta",
    "Thuong ta",
    "Dai ta",
]

# Ten hien thi co dau cho cap bac (dung cho giao dien)
RANK_DISPLAY = {
    "Thieu uy": "Thiếu úy",
    "Trung uy": "Trung úy",
    "Thuong uy": "Thượng úy",
    "Dai uy": "Đại úy",
    "Thieu ta": "Thiếu tá",
    "Trung ta": "Trung tá",
    "Thuong ta": "Thượng tá",
    "Dai ta": "Đại tá",
}

# Danh sach gia tri de luu trong CSDL (dung chuoi co dau, don gian cho form chon)
RANK_CHOICES = [
    "Thiếu úy",
    "Trung úy",
    "Thượng úy",
    "Đại úy",
    "Thiếu tá",
    "Trung tá",
    "Thượng tá",
    "Đại tá",
    "Chuẩn đô đốc/Thiếu tướng",
    "Khác",
]

# So nam toi thieu tu cap bac X len cap bac ke tiep
RANK_YEARS_TO_NEXT = {
    "Thiếu úy": 2,
    "Trung úy": 3,
    "Thượng úy": 3,
    "Đại úy": 4,
    "Thiếu tá": 4,
    "Trung tá": 4,
    "Thượng tá": 4,
}

RANK_NEXT = {
    "Thiếu úy": "Trung úy",
    "Trung úy": "Thượng úy",
    "Thượng úy": "Đại úy",
    "Đại úy": "Thiếu tá",
    "Thiếu tá": "Trung tá",
    "Trung tá": "Thượng tá",
    "Thượng tá": "Đại tá",
}

GENDER_CHOICES = ["Nam", "Nữ"]

PARTY_SYMPATHY_CHOICES = ["Có", "Không"]

# 4 muc quan ly du lieu nhan su (muc thu 5 "Thong ke" khong gan voi 1 category du lieu)
CATEGORY_DOMESTIC = "trong_nuoc"
CATEGORY_FOREIGN = "ngoai_nuoc"
CATEGORY_CADRE = "quan_so_khung"
CATEGORY_ARCHIVE = "ho_so_luu"

CATEGORY_CHOICES = [
    (CATEGORY_DOMESTIC, "Quản lý học viên trong nước"),
    (CATEGORY_FOREIGN, "Quản lý học viên ngoài nước"),
    (CATEGORY_CADRE, "Quản lý quân số khung"),
    (CATEGORY_ARCHIVE, "Quản lý hồ sơ lưu"),
]

CATEGORY_LABELS = dict(CATEGORY_CHOICES)

CATEGORY_SINGULAR = {
    CATEGORY_DOMESTIC: "học viên trong nước",
    CATEGORY_FOREIGN: "học viên ngoài nước",
    CATEGORY_CADRE: "quân số khung",
    CATEGORY_ARCHIVE: "hồ sơ lưu",
}

EDUCATION_LEVEL_CHOICES = [
    "NCS (Nghiên cứu sinh)",
    "CH (Cao học)",
    "ĐH (Đại học)",
    "VB2 (Văn bằng 2)",
    "CK2 (Chuyên khoa 2)",
]

# --- Danh sach truong hien thi trong bang danh sach (dung cho che do Day du / Rut gon) ---
# Moi phan tu: (ma truong, nhan hien thi, loai du lieu: text|date|badge)
PERSONNEL_LIST_FIELDS = [
    ("full_name", "Họ và tên", "text"),
    ("gender", "Giới tính", "text"),
    ("date_of_birth", "Ngày sinh", "date"),
    ("ethnicity", "Dân tộc", "text"),
    ("religion", "Tôn giáo", "text"),
    ("enlistment_date", "Ngày nhập ngũ", "date"),
    ("rank", "Cấp bậc", "text"),
    ("rank_date", "TG nhận cấp bậc", "date"),
    ("position", "Chức vụ", "text"),
    ("position_date", "TG nhận chức vụ", "date"),
    ("youth_union_date", "TG vào Đoàn", "date"),
    ("party_join_date", "TG vào Đảng", "date"),
    ("party_official_date", "TG chính thức", "date"),
    ("school_name", "Trường theo học", "text"),
    ("major", "Chuyên ngành", "text"),
    ("education_level", "Bậc học", "text"),
    ("graduation_date", "TG tốt nghiệp", "date"),
    ("hometown", "Quê quán", "text"),
    ("current_residence", "Nơi ở", "text"),
    ("phone", "Số điện thoại", "text"),
]

# Cac truong mac dinh hien thi trong che do "Rut gon"
DEFAULT_COMPACT_FIELDS = [
    "full_name",
    "gender",
    "date_of_birth",
    "rank",
    "position",
    "party_join_date",
]

# Khoa cau hinh luu trong bang app_settings
SETTING_COMPACT_FIELDS = "personnel_compact_fields"

ROLE_ADMIN = "admin"
ROLE_MOD = "mod"
ROLE_VIEWER = "viewer"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Quản trị viên (Admin)"),
    (ROLE_MOD, "Biên tập viên (Mod)"),
    (ROLE_VIEWER, "Chỉ xem (Viewer)"),
]

ROLE_LABELS = dict(ROLE_CHOICES)
