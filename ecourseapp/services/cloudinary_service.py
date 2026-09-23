import os
import mimetypes
import tempfile
import cloudinary
import cloudinary.uploader

# Cấu hình tự động đọc từ biến môi trường
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_file(filepath, filename=None):
    """
    Hàm upload đa năng cho cả Ảnh, Video và PDF lên Cloudinary.
    Giữ nguyên signature trả về (public_id, secure_url) tương thích với DB cũ.
    """
    try:
        mime_type, _ = mimetypes.guess_type(filepath)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Tự động xác định resource_type
        if mime_type.startswith("video/"):
            res_type = "video"
            folder = "ecourse/videos"
            # Dùng upload_large cho video để upload ổn định dạng chunk
            res = cloudinary.uploader.upload_large(
                filepath,
                resource_type=res_type,
                folder=folder,
                chunk_size=6000000
            )
        elif mime_type.startswith("image/"):
            res_type = "image"
            folder = "ecourse/images"
            res = cloudinary.uploader.upload(
                filepath,
                resource_type=res_type,
                folder=folder
            )
        else:
            # File PDF, tài liệu
            res_type = "raw"
            folder = "ecourse/docs"
            res = cloudinary.uploader.upload(
                filepath,
                resource_type=res_type,
                folder=folder
            )

        public_id = res.get("public_id")
        file_url = res.get("secure_url")
        return public_id, file_url

    except Exception as e:
        print(f"[Cloudinary Upload Error]: {e}")
        return None, None


def delete_file(public_id, resource_type="image"):
    """Xóa file khỏi Cloudinary"""
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    except Exception as e:
        print(f"[Cloudinary Delete Error]: {e}")


def replace_drive_file(obj, drive_id_field, url_field, file_storage, filename=None):
    """Hàm giữ nguyên tương thích ngược với các module DAO cũ"""
    old_public_id = getattr(obj, drive_id_field, None)

    filename = filename or file_storage.filename
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file_storage.save(tmp.name)
        tmp_path = tmp.name

    try:
        new_id, new_url = upload_file(tmp_path, filename)
        if new_id is None:
            return obj
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if old_public_id:
        delete_file(old_public_id)

    setattr(obj, drive_id_field, new_id)
    setattr(obj, url_field, new_url)
    return obj