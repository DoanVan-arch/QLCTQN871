# -*- coding: utf-8 -*-
"""Tien ich luu/xoa file minh chung (anh/pdf) khen thuong."""
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EVIDENCE_EXTENSIONS", set())


def save_evidence_file(file_storage):
    """Luu file upload, tra ve ten file da luu (duy nhat) hoac None neu khong co file."""
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(file_storage.filename.rsplit(".", 1)[0])
    stored_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)
    file_storage.save(path)
    return stored_name


def delete_evidence_file(stored_name):
    if not stored_name:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def is_pdf(stored_name):
    return bool(stored_name) and stored_name.lower().endswith(".pdf")
