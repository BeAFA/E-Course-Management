import os
import mimetypes
import tempfile
import traceback

from google.oauth2 import service_account
from google.auth.transport.requests import Request as GoogleAuthRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Đường dẫn an toàn trỏ thẳng vào file drive_key.json
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.abspath(os.path.join(CURRENT_DIR, "..", "credentials", "drive_key.json"))

FOLDER_ID = "1jwBv0BUqeq9MoQzpYp_10AfX2G96QN8V"

credentials = service_account.Credentials.from_service_account_file(
    KEY_PATH, scopes=SCOPES
)

def get_drive_service():
    global credentials
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())
    return build("drive", "v3", credentials=credentials)

def upload_file(filepath, filename):
    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = "application/octet-stream"

    metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }

    try:
        service = get_drive_service()

        media = MediaFileUpload(
            filepath,
            mimetype=mime_type,
            resumable=True,
            chunksize=5 * 1024 * 1024
        )

        # Upload file lên thư mục
        file = service.files().create(
            body=metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = file.get("id")

        # Cấp quyền xem công khai (bọc riêng để nếu lỗi không làm hỏng cả luồng upload)
        try:
            service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"}
            ).execute()
        except Exception as perm_err:
            print("Cảnh báo public_file:", perm_err)

        if mime_type.startswith("image/"):
            url = f"https://lh3.googleusercontent.com/d/{file_id}"
        else:
            url = f"https://drive.google.com/file/d/{file_id}/preview"

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
            body=permission,
            supportsAllDrives=True
        ).execute()
    except Exception as e:
        print(f"Cảnh báo khi public file {file_id}:", e)


def get_preview_url(file_id):
    return f"https://drive.google.com/file/d/{file_id}/preview"


def delete_file(file_id):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
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