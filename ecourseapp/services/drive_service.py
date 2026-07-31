from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "credentials/drive_key.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

drive_service = build(
    "drive",
    "v3",
    credentials=credentials
)

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
        print(e)
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
