import os
import requests
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, Response, stream_with_context, jsonify, url_for
from google.auth.transport.requests import Request as GoogleAuthRequest
from werkzeug.utils import secure_filename

from __init__ import app, db, login
from services.drive_service import upload_file, credentials
from models import User, UserRole, Level, Lesson, Chapter, Course, Tag, CourseTag
import dao

import admin

TEMP_UPLOAD_DIR = "temp"

# Bạn có thể định nghĩa các hằng số này ở đầu file hoặc trong file config
DEFAULT_AVATAR_DRIVE_ID = "1X-nx8rzQBGGg676PHve-0J-KGYpjJj-1"
# Tạo link trực tiếp để hiển thị ảnh từ Google Drive
DEFAULT_AVATAR_URL = f"https://drive.google.com/uc?id={DEFAULT_AVATAR_DRIVE_ID}"

# Bạn có thể định nghĩa các hằng số này ở đầu file hoặc trong file config
DEFAULT_COURSE_IMG_DRIVE_ID = "1AvAw7sucIgoV3ytOruFTTEeEt6YOQQY9"
# Tạo link trực tiếp để hiển thị ảnh từ Google Drive
DEFAULT_COURSE_IMG_URL = f"https://drive.google.com/uc?id={DEFAULT_COURSE_IMG_DRIVE_ID}"

# Bạn có thể định nghĩa các hằng số này ở đầu file hoặc trong file config
DEFAULT_LESSON_IMG_DRIVE_ID = "1DaVBg8l_Ze_b6CB0-4ThfxmIxpxE-ojU"
# Tạo link trực tiếp để hiển thị ảnh từ Google Drive
DEFAULT_LESSON_IMG_URL = f"https://drive.google.com/uc?id={DEFAULT_LESSON_IMG_DRIVE_ID}"


@app.route('/')
def home():
    kw = request.args.get('kw')
    category_id = request.args.get('category_id')

    courses = dao.get_courses(kw=kw, category_id=category_id)
    return render_template('home.html', courses=courses)


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=["GET", "POST"])
def login_my_user():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = dao.auth_user(email, password)

        if user:
            login_user(user)
            if user.role == UserRole.STUDENT:
                return redirect('/')
            if user.role == UserRole.TEACHER:
                return redirect('/')
            elif user.role == UserRole.ADMIN:
                return redirect('/admin/')
            return redirect('/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng!"
            return render_template("login.html", err_msg=err_msg)

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register_new_user():
    # Chỉnh sửa thêm nghiệp vụ đăng ký cho giảng viên
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        role = request.form.get("role")

        # 1. KIỂM TRA DỮ LIỆU ĐẦU VÀO
        if password != confirm:
            return render_template("register.html", err_msg="Xác nhận mật khẩu không khớp!")

        existing_user = User.query.filter(User.email == email).first()
        if existing_user:
            return render_template("register.html", err_msg="Tài khoản này đã được đăng ký")

        # 2. XỬ LÝ HÌNH ẢNH
        # Gán sẵn ID và URL của file user.png trên Drive của bạn làm mặc định
        img_drive_id = DEFAULT_AVATAR_DRIVE_ID
        img_url = DEFAULT_AVATAR_URL

        img = request.files.get("img")

        # Nếu người dùng có upload file ảnh mới (filename không rỗng)
        if img and img.filename != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            # Tải ảnh mới của người dùng lên Drive
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                return render_template("register.html", err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại.")

            # Ghi đè lại ảnh mặc định bằng ảnh người dùng vừa upload thành công
            img_drive_id = uploaded_id
            img_url = uploaded_url

        # 3. LƯU DATABASE
        try:
            hashed_password = generate_password_hash(password)
            user = User(
                name=name,
                email=email,
                password=hashed_password,
                role=UserRole(role),
                img_drive_id=img_drive_id,  # Sẽ lưu ID mặc định hoặc ID vừa upload
                img_url=img_url  # Sẽ lưu URL mặc định hoặc URL vừa upload
            )
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except Exception as ex:
            db.session.rollback()
            print(f"Database error: {ex}")
            return render_template("register.html", err_msg="Hệ thống đã bị lỗi! Xin vui lòng thử lại sau")

    return render_template("register.html")


@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect('/')


@app.route('/profile')
def profile_my_user():
    if not current_user.is_authenticated:
        return redirect("/login")

    levels = list(Level)
    return render_template("profile.html", levels=levels)


@app.route('/profile/updateprofile', methods=["POST"])
def update_profile():
    if not current_user.is_authenticated:
        return redirect("/login")

    levels = list(Level)
    try:
        current_user.name = request.form["name"]
        if request.form.get("level"):
            current_user.level = Level(request.form.get("level"))
        current_user.major = request.form["major"]

        db.session.commit()
        return redirect('/profile')
    except Exception as ex:
        db.session.rollback()
        print(ex)

        err_msg = "Hệ thống đã bị lỗi! Xin vui lòng thử lại sau"
        return render_template("profile.html", levels=levels, err_msg=err_msg)


@app.route('/profile/updatepass', methods=["GET", "POST"])
def update_password():
    if not current_user.is_authenticated:
        return redirect("/login")

    if request.method == "POST":
        oldpassword = request.form.get('oldpassword')
        newpassword = request.form.get("newpassword")
        confirm = request.form.get("confirm")

        if check_password_hash(current_user.password, oldpassword):
            if check_password_hash(current_user.password, newpassword):
                err_msg = "Mật khẩu mới phải khác mật khẩu cũ"
                return render_template("change_password.html", user=current_user, err_msg=err_msg)
            if newpassword != confirm:
                err_msg = "Xác nhận mật khẩu không đúng"
                return render_template("change_password.html", user=current_user, err_msg=err_msg)
            try:
                current_user.password = generate_password_hash(newpassword)
                db.session.commit()
                return redirect('/profile')
            except Exception as ex:
                db.session.rollback()
                print(ex)

                err_msg = "Hệ thống đã bị lỗi! Xin vui lòng thử lại sau"
                return render_template("change_password.html", user=current_user, err_msg=err_msg)
        else:
            err_msg = "Mật khẩu cũ không đúng!"
        return render_template("change_password.html", user=current_user, err_msg=err_msg)

    return render_template("change_password.html", user=current_user)


@app.route('/courses')
def get_all_courses():
    courses = dao.get_courses()
    return render_template("chapter.html", courses=courses)


@app.route('/courses/my_courses')
def get_my_course():
    if not current_user.is_authenticated and current_user.role != UserRole.TEACHER:
        err_msg = "Bạn không có quyền truy cập!"
        return render_template("home.html", err_msg=err_msg)
    courses = dao.get_my_courses(current_user.id)
    for c in courses:
        c.tag_names = dao.get_course_tag(c.id)
    return render_template("my_courses.html", courses=courses)


@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = dao.get_course_by_id(course_id)
    if not course:
        return redirect('/')

    stats = dao.get_course_rating_stats(course_id)
    ratings_page = dao.get_ratings_by_course(course_id, page=request.args.get('page', 1, type=int))
    is_owner = dao.is_course_owner(current_user, course)

    return render_template(
        'course_detail.html',
        course=course,
        is_owner=is_owner,
        avg_rating=stats['avg_rating'],
        rating_count=stats['rating_count'],
        ratings=ratings_page.items,
        pagination=ratings_page,
    )


@app.route('/courses/<int:course_id>/rate', methods=['POST'])
def rate_course(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    rating_value = int(request.form.get('rating', 5))
    comment = request.form.get('comment')

    rating, err = dao.add_or_update_rating(current_user.id, course_id, rating_value, comment)
    if err:
        # có thể flash message thay vì render tay
        pass

    return redirect(f'/courses/{course_id}')


@app.route('/courses/create', methods=['GET', 'POST'])
def create_course():
    err_msg = ""
    # Xóa các comment ở dưới nếu muốn kiểm tra đăng nhập và quyền
    # if not current_user.is_authenticated:
    #     return redirect('/login')

    # if current_user.role != UserRole.TEACHER:
    #     err_msg = "Yêu cầu tài khoản với quyền là giảng viên"

    categories = dao.get_categories()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        # tag_ids = request.form.getlist("tag_ids")

        img_drive_id = DEFAULT_COURSE_IMG_DRIVE_ID
        img_url = DEFAULT_COURSE_IMG_URL

        img = request.files.get("img")
        if img and img.filename != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            # Tải ảnh mới của người dùng lên Drive
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                return render_template("create_course.html", err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại.")

            # Ghi đè lại ảnh mặc định bằng ảnh người dùng vừa upload thành công
            img_drive_id = uploaded_id
            img_url = uploaded_url

        if not name or not category_id:
            err_msg = "Vui lòng nhập tên khóa học và chọn danh mục!"
        else:
            try:
                new_course = dao.create_course(
                    name=name,
                    price=price,
                    category_id=category_id,
                    description=description,
                    teacher_id=current_user.id,
                    img_drive_id=img_drive_id,
                    img_url=img_url
                    # tag_ids=tag_ids
                )
                return redirect(f'/courses/{new_course.id}')
            except Exception as ex:
                db.session.rollback()
                print(ex)
                err_msg = "Có lỗi xảy ra khi đăng khóa học. Vui lòng thử lại sau!"
    return render_template('create_course.html', categories=categories, err_msg=err_msg)


@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def update_course(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    err_msg = ""
    course = dao.get_course_by_id(course_id)
    if not dao.is_course_owner(current_user, course):
        err_msg = "Bạn không có quyền chỉnh sửa khóa học này"
        return render_template("home.html", err_msg=err_msg)

    if course is None:
        err_msg="Khóa học không tồn tại"
        return render_template("my_course.html", err_msg=err_msg)

    categories = dao.get_categories()

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        # tag_ids = request.form.getlist("tag_ids")

        img_drive_id = course.img_drive_id
        img_url = course.img_url

        img = request.files.get("img")
        if img and img.filename != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            # Tải ảnh mới của người dùng lên Drive
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại."
                return render_template("create_course.html", course=course, categories=categories, err_msg=err_msg)

            # Ghi đè lại ảnh mặc định bằng ảnh người dùng vừa upload thành công
            img_drive_id = uploaded_id
            img_url = uploaded_url

        if not name or not category_id:
            err_msg = "Vui lòng nhập tên khóa học và chọn danh mục!"
            return render_template('create_course.html', course=course, categories=categories, err_msg=err_msg)
        try:
            dao.update_course(course,name,price,category_id,description,img_drive_id,img_url, tag_ids=None)
            db.session.commit()
            return redirect(f'/courses/{course.id}')
        except Exception as ex:
            db.session.rollback()
            print(ex)
            err_msg = "Có lỗi xảy ra khi đăng khóa học. Vui lòng thử lại sau!"
            return render_template('create_course.html', course=course, categories=categories, err_msg=err_msg)

    return render_template('create_course.html', course=course, categories=categories, err_msg=err_msg)

@app.route('/courses/bulk-update-status', methods=['POST'])
def bulk_update_course_status():
    if not current_user.is_authenticated:
        return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401

    data = request.get_json()
    course_ids = data.get('course_ids', [])
    is_active = data.get('is_active')

    if not course_ids or is_active is None:
        return jsonify({"success": False, "message": "Dữ liệu không hợp lệ"}), 400

    try:
        dao.bulk_update_active(course_ids, is_active, current_user.id)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as ex:
        db.session.rollback()
        print(ex)
        return jsonify({"success": False, "message": "Có lỗi xảy ra, vui lòng thử lại"}), 500


@app.route('/courses/<int:course_id>/chapters/add', methods=["GET", "POST"])
def add_chapters(course_id):
    course = dao.get_course_by_id(course_id)
    if not current_user.is_authenticated or not dao.is_course_owner(current_user, course):
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            return render_template("create_chapter.html", course_id=course_id,
                                   err_msg="Bạn phải đặt tên cho chương")

        chapter = Chapter(
            name=name,
            description=description,
            course_id=course_id,
        )

        try:
            db.session.add(chapter)
            db.session.commit()
            return redirect(f"/courses/{course_id}")

        except Exception as ex:
            db.session.rollback()
            print(ex)
            return "Upload failed"

    chapter_list = db.session.query(Chapter).filter(Chapter.course_id == course_id).all()
    return render_template("create_chapter.html", chapters=chapter_list, course_id=course_id)

@app.route('/courses/<int:course_id>/chapters/<int:chapter_id>/update', methods=["GET", "POST"])
def update_chapters(course_id, chapter_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    course = dao.get_course_by_id(course_id)
    is_owner = dao.is_course_owner(current_user, course)
    if not dao.is_course_owner(current_user, course):
        return render_template("course_detail.html", course=course, is_owner=is_owner,
                                err_msg="Bạn không có quyền chỉnh sửa khóa học này")

    chapter = dao.get_chapter_by_id(chapter_id)
    if chapter is None or chapter.course_id != course_id:
        return render_template("course_detail.html", course=course,
                                is_owner=is_owner, err_msg="Chương này không tồn tại")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            chapter.name = name
            chapter.description = description
            return render_template("create_chapter.html", chapter=chapter,
                                   course_id=course_id,
                                   err_msg="Bạn phải đặt tên cho chương")
        try:
            dao.update_chapter(chapter, name, description)
            db.session.commit()
            return redirect(url_for('course_detail', course_id=course_id))
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return "Upload failed"

    chapter_list = db.session.query(Chapter).filter(Chapter.course_id == course_id).all()
    return render_template("create_chapter.html", chapter=chapter,
                            chapters=chapter_list, course_id=course_id)



@app.route('/chapters/<int:chapter_id>/lessons')
def lessons(chapter_id):
    chapter = dao.get_chapter_by_id(chapter_id)
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")
    lesson_list = db.session.query(Lesson).filter(Lesson.chapter_id == chapter_id).all()
    return render_template("lesson.html", lessons=lesson_list, chapter_id=chapter_id)


@app.route("/chapters/<int:chapter_id>/lessons/add", methods=["GET", "POST"])
def add_lesson(chapter_id):
    chapter = dao.get_chapter_by_id(chapter_id)
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")

    if request.method == "POST":
        os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

        video = request.files.get("video")
        video_drive_id = None
        video_url = None
        if video and video.filename:
            filename = secure_filename(video.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            video.save(filepath)
            video_drive_id, video_url = upload_file(filepath, filename)
            os.remove(filepath)

            if video_drive_id is None:
                return render_template(
                    "create_lesson.html",
                    chapter_id=chapter_id,
                    err_msg="Tải video lên Drive thất bại, vui lòng thử lại."
                )

        pdf_file = request.files.get("pdf")
        file_drive_id = None
        file_url = None
        if pdf_file and pdf_file.filename:
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            pdf_file.save(filepath)
            file_drive_id, file_url = upload_file(filepath, filename)
            os.remove(filepath)

            if file_drive_id is None:
                return render_template(
                    "create_lesson.html",
                    chapter_id=chapter_id,
                    err_msg="Tải tài liệu PDF lên Drive thất bại, vui lòng thử lại."
                )

        # 2. XỬ LÝ HÌNH ẢNH
        # Gán sẵn ID và URL của file user.png trên Drive của bạn làm mặc định
        img_drive_id = DEFAULT_LESSON_IMG_DRIVE_ID
        img_url = DEFAULT_LESSON_IMG_URL

        img = request.files.get("img")

        # Nếu người dùng có upload file ảnh mới (filename không rỗng)
        if img and img.filename != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            # Tải ảnh mới của người dùng lên Drive
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                return render_template("create_lesson.html",
                                       err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại.")

            # Ghi đè lại ảnh mặc định bằng ảnh người dùng vừa upload thành công
            img_drive_id = uploaded_id
            img_url = uploaded_url

        lesson = Lesson(
            chapter_id=chapter_id,
            title=request.form["title"],
            video_drive_id=video_drive_id,
            video_url=video_url,
            file_drive_id=file_drive_id,
            file_url=file_url,
            article=request.form.get("article"),
            img_drive_id=img_drive_id,
            img_url=img_url
        )

        try:
            db.session.add(lesson)
            db.session.commit()
            return redirect(f"/chapters/{chapter_id}/lessons")

        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template(
                "create_lesson.html",
                chapter_id=chapter_id,
                err_msg="Lưu bài học thất bại, vui lòng thử lại."
            )

    return render_template("create_lesson.html", chapter_id=chapter_id)


@app.route("/lessons/<int:lesson_id>", methods=["GET", "POST"])
def lesson_detail(lesson_id):
    lesson = dao.get_lesson_by_id(lesson_id)
    if not current_user.is_authenticated or not dao.is_lesson_owner(current_user, lesson):
        return redirect("/")
    return render_template("lesson_detail.html", lesson=lesson)


@app.route("/lessons/<int:lesson_id>/update", methods=["GET", "POST"])
def update_lesson(lesson_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    lesson = dao.get_lesson_by_id(lesson_id)
    is_owner = dao.is_lesson_owner(current_user, lesson)
    if not is_owner:
        return render_template("course_detail.html", course_id=lesson.chapter.course_id,
                               is_owner=is_owner, err_msg="Bạn không có quyền chỉnh sửa khóa học này")

    chapter = dao.get_chapter_by_id(lesson.chapter_id)
    if lesson is None or lesson.chapter_id != chapter.id:
        return render_template("course_detail.html", course=lesson.chapter.course_id,
                               is_owner=is_owner, err_msg="Chương này không tồn tại")

    if request.method == "POST":
        title = request.form.get("title")
        if not title or title.strip() == "":
            return render_template("create_lesson.html", lesson_id=lesson.id, lesson=lesson,
                                   err_msg="Bạn phải đặt tiêu đề cho bài giảng của mình")

        os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

        video_drive_id = lesson.video_drive_id
        video_url = lesson.video_url
        video = request.files.get("video")
        if video and video.filename:
            filename = secure_filename(video.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            video.save(filepath)
            video_drive_id, video_url = upload_file(filepath, filename)
            os.remove(filepath)

            if video_drive_id is None:
                return render_template("create_lesson.html", lesson_id=lesson.id, lesson=lesson,
                                       err_msg="Tải video lên Drive thất bại, vui lòng thử lại.")

        img_drive_id = lesson.img_drive_id
        img_url = lesson.img_url
        img = request.files.get("img")
        if img and img.filename != '':
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                return render_template("create_lesson.html", lesson_id=lesson.id, lesson=lesson,
                                       err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại.")

            img_drive_id = uploaded_id
            img_url = uploaded_url

        article = request.form.get("article")

        lesson.title = title
        lesson.video_drive_id = video_drive_id
        lesson.video_url = video_url
        lesson.article = article
        lesson.img_drive_id = img_drive_id
        lesson.img_url = img_url

        try:
            db.session.commit()
            return redirect(f"/chapters/{lesson.chapter_id}/lessons")
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template("create_lesson.html", lesson_id=lesson.id, lesson=lesson,
                                   err_msg="Lưu bài học thất bại, vui lòng thử lại.")

    return render_template("create_lesson.html", lesson_id=lesson.id, lesson=lesson,
                           chapter_id=lesson.chapter_id)


@app.route("/media/video/<file_id>")
def stream_video(file_id):
    # Làm mới access token nếu đã hết hạn
    if not credentials.valid:
        credentials.refresh(GoogleAuthRequest())

    drive_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    headers = {"Authorization": f"Bearer {credentials.token}"}

    # Chuyển tiếp header Range (để hỗ trợ tua video) từ trình duyệt sang Drive
    range_header = request.headers.get("Range")
    if range_header:
        headers["Range"] = range_header

    r = requests.get(drive_url, headers=headers, stream=True)

    resp = Response(
        stream_with_context(r.iter_content(chunk_size=8192)),
        status=r.status_code,
        content_type=r.headers.get("Content-Type", "video/mp4"),
    )

    if "Content-Range" in r.headers:
        resp.headers["Content-Range"] = r.headers["Content-Range"]
    if "Content-Length" in r.headers:
        resp.headers["Content-Length"] = r.headers["Content-Length"]

    resp.headers["Accept-Ranges"] = "bytes"
    resp.headers["Content-Disposition"] = "inline"  # ép phát trực tiếp, không tải file

    return resp


if __name__ == '__main__':
    app.run(debug=True)
