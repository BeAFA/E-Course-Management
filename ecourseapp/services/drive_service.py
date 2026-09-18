import os
import mimetypes
import tempfile
import traceback

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials", "Test_User.txt")


def _load_oauth_config(path):
    config = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            config[key.strip()] = value.strip()
    required = ["refresh_token", "client_id", "client_secret"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Thiếu thông tin trong {path}: {missing}")
    return config


_cfg = _load_oauth_config(TOKEN_FILE)

credentials = Credentials(
    token=None,
    refresh_token=_cfg["refresh_token"],
    client_id=_cfg["client_id"],
    client_secret=_cfg["client_secret"],
    token_uri="https://oauth2.googleapis.com/token",
    scopes=SCOPES,
)

FOLDER_ID = "1jwBv0BUqeq9MoQzpYp_10AfX2G96QN8V"


def get_drive_service():
    """Luôn làm mới token nếu đã hết hạn trước khi gọi API"""
    if credentials.expired or not credentials.valid:
        credentials.refresh(Request())
    return build("drive", "v3", credentials=credentials)


def upload_file(filepath, filename):
    # Xác định đúng mimetype (video/mp4, image/jpeg, application/pdf...)
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = "application/octet-stream"

    metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }
    
    try:
        service = get_drive_service()

        # chunksize 5MB giúp upload video lớn ổn định và không ngắt kết nối giữa chừng
        media = MediaFileUpload(
            filepath,
            mimetype=mime_type,
            resumable=True,
            chunksize=5 * 1024 * 1024
        )

        file = service.files().create(
            body=metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file["id"]
        public_file(file_id)
        url = get_preview_url(file_id)
        return file_id, url

    except HttpError as e:
        print("[Drive HTTP Error]:", e.content.decode("utf-8") if hasattr(e, "content") else e)
        traceback.print_exc()
        return None, None
    except Exception as e:
        print("[Unexpected upload error]:", e)
        traceback.print_exc()
        return None, None


def public_file(file_id):
    try:
        service = get_drive_service()
        permission = {
            "type": "anyone",
            "role": "reader"
        }
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
    except Exception as e:
        print(f"Cảnh báo khi public file {file_id}:", e)


def get_preview_url(file_id):
    return f"https://drive.google.com/file/d/{file_id}/preview"


def delete_file(file_id):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()
    except HttpError as e:
        print(f"Không thể xóa file {file_id} trên Drive:", e)


def replace_drive_file(obj, drive_id_field, url_field, file_storage, filename=None):
    old_file_id = getattr(obj, drive_id_field, None)

    filename = filename or file_storage.filename
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        tmp_path = tmp.name

    try:
        new_file_id, new_url = upload_file(tmp_path, filename)
        if new_file_id is None:
            return obj
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if old_file_id:
        delete_file(old_file_id)

    setattr(obj, drive_id_field, new_file_id)
    setattr(obj, url_field, new_url)

    return obj