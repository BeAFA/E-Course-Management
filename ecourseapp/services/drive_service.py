import os
import tempfile

from google.oauth2.credentials import Credentials
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

drive_service = build("drive", "v3", credentials=credentials)

FOLDER_ID = "1jwBv0BUqeq9MoQzpYp_10AfX2G96QN8V"


def upload_file(filepath, filename):
    metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }
    try:
        media = MediaFileUpload(filepath, resumable=True)

        file = drive_service.files().create(
            body=metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file["id"]
        public_file(file_id)
        url = get_preview_url(file_id)

    except HttpError as e:
        print("Drive upload error:", e)
        return None, None
    except Exception as e:
        print("Unexpected upload error:", e)
        return None, None

    return file_id, url


def public_file(file_id):
    permission = {
        "type": "anyone",
        "role": "reader"
    }
    drive_service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()


def get_preview_url(file_id):
    return f"https://drive.google.com/file/d/{file_id}/preview"


def delete_file(file_id):
    drive_service.files().delete(
        fileId=file_id
    ).execute()

def replace_drive_file(obj, drive_id_field, url_field, file_storage, filename=None):
    """
    Thay thế file (ảnh/video/...) cũ trên Drive bằng file mới cho 1 object bất kỳ.

    obj: đối tượng model (vd: Lesson, User, Course...) đã có 2 field
         <drive_id_field> và <url_field>
    drive_id_field: tên field lưu file_id trên Drive (vd: "video_drive_id")
    url_field: tên field lưu url preview (vd: "video_url")
    file_storage: file upload từ request (werkzeug FileStorage, vd request.files['video'])
    filename: tên file muốn lưu trên Drive (mặc định lấy tên gốc)
    """
    old_file_id = getattr(obj, drive_id_field, None)

    # Lưu file tạm ra ổ đĩa vì MediaFileUpload cần path
    filename = filename or file_storage.filename
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        tmp_path = tmp.name

    try:
        new_file_id, new_url = upload_file(tmp_path, filename)
        if new_file_id is None:
            # upload thất bại -> không đụng gì tới file cũ, giữ nguyên object
            return obj
    finally:
        os.remove(tmp_path)

    # Upload mới thành công thì mới xóa file cũ (tránh mất dữ liệu nếu upload lỗi)
    if old_file_id:
        try:
            delete_file(old_file_id)
        except HttpError as e:
            print("Không xóa được file cũ trên Drive:", e)

    setattr(obj, drive_id_field, new_file_id)
    setattr(obj, url_field, new_url)

    return obj
