import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "doi-871-chinh-tri-quan-nhan-secret-key-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "qlctqn871.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # So thang canh bao truoc khi den han (thang) de hien thi "sap den han"
    WARNING_MONTHS_AHEAD = 3

    # Thu muc luu file minh chung khen thuong (anh/pdf)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads", "rewards")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # toi da 10MB moi file
    ALLOWED_EVIDENCE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}
