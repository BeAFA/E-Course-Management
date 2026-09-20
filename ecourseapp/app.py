import json
import os
from datetime import datetime, timezone

import admin
import requests
from flask import render_template, request, redirect, Response, stream_with_context, jsonify, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from flask_socketio import SocketIO, emit, join_room
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.genai import types
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from __init__ import app, db, login, client, GEMINI_MODEL, SYSTEM_INSTRUCTION, VNPAY_CONFIG
from ai_chat_routes import RESPONSE_SCHEMA, _build_courses_context, MAX_TURNS_SENT, _serialize_message
from models import (
    User, UserRole, Level, Lesson, Chapter, Course, Tag, CourseTag,
    ChatRoom, ChatRoomMessage, Question, Test, Choice, UserTest,
    CourseRecommendation, SenderType, AIChatRoomMessage, AIChatRoom
)
import dao
from vnpay import vnpay

TEMP_UPLOAD_DIR = "temp"

from services.cloudinary_service import upload_file, delete_file

# Ảnh mặc định chuyển sang link mẫu sẵn của Cloudinary hoặc static nội bộ
DEFAULT_AVATAR_DRIVE_ID = "default_avatar"
DEFAULT_AVATAR_URL = "https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg"

DEFAULT_COURSE_IMG_DRIVE_ID = "default_course"
DEFAULT_COURSE_IMG_URL = "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&auto=format&fit=crop"

DEFAULT_LESSON_IMG_DRIVE_ID = "default_lesson"
DEFAULT_LESSON_IMG_URL = "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=600&auto=format&fit=crop"

MAX_MESSAGE_LENGTH = 500

socketio = SocketIO(app, cors_allowed_origins="*")


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
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        role = request.form.get("role")

        if role is None:
            role = "STUDENT"

        if password != confirm:
            return render_template("register.html", err_msg="Xác nhận mật khẩu không khớp!")

        existing_user = User.query.filter(User.email == email).first()
        if existing_user:
            return render_template("register.html", err_msg="Tài khoản này đã được đăng ký")

        img_drive_id = DEFAULT_AVATAR_DRIVE_ID
        img_url = DEFAULT_AVATAR_URL

        img = request.files.get("img")
        if img and img.filename != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                return render_template("register.html", err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại.")

            img_drive_id = uploaded_id
            img_url = uploaded_url

        try:
            hashed_password = generate_password_hash(password)
            user = User(
                name=name,
                email=email,
                password=hashed_password,
                role=UserRole(role),
                img_drive_id=img_drive_id,
                img_url=img_url
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
    kw = request.args.get('kw')
    rating_min = request.args.get('rating')
    price_sort = request.args.get('price_sort')
    category_id = request.args.get('category_id')
    ids_param = request.args.get('ids')

    course_ids = None
    if ids_param:
        course_ids = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]

    categories = dao.get_categories()

    courses = dao.get_courses(
        kw=kw,
        category_id=category_id,
        rating_min=rating_min,
        price_sort=price_sort,
        course_ids=course_ids
    )

    return render_template(
        "courses.html",
        courses=courses,
        categories=categories,
        is_ai_recommendation=bool(ids_param),
        no_ai_history=request.args.get('no_ai_history')
    )


@app.route('/courses/recommended')
def view_recommended_courses():
    if not current_user.is_authenticated:
        return redirect(url_for('login_my_user', next=request.url))

    course_ids = dao.get_recommended_course_ids_for_user(current_user.id)
    if not course_ids:
        return redirect(url_for('get_all_courses', no_ai_history=1))

    ids_str = ",".join(str(i) for i in course_ids)
    return redirect(url_for('get_all_courses', ids=ids_str))


@app.route('/courses/recommended/dismiss', methods=['POST'])
def dismiss_recommended_courses():
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    data = request.get_json(force=True)
    raw_ids = data.get('course_ids', [])

    try:
        course_ids = [int(cid) for cid in raw_ids]
    except (TypeError, ValueError):
        return jsonify({"error": "Danh sách ID không hợp lệ"}), 400

    if not course_ids:
        return jsonify({"error": "Chưa chọn khóa học nào"}), 400

    try:
        dao.dismiss_recommended_courses(current_user.id, course_ids)
        return jsonify({"success": True, "removed": course_ids})
    except Exception as ex:
        db.session.rollback()
        print(ex)
        return jsonify({"error": "Có lỗi xảy ra, vui lòng thử lại"}), 500


@app.route('/courses/my_courses')
def get_my_course():
    if not current_user.is_authenticated or current_user.role != UserRole.TEACHER:
        err_msg = "Bạn không có quyền truy cập!"
        return render_template("home.html", err_msg=err_msg)
    courses = dao.get_my_courses(current_user.id)
    for c in courses:
        c.tag_names = dao.get_course_tag(c.id)
    return render_template("my_courses.html", courses=courses)


@app.route('/my_enrolled_courses')
@login_required
def my_enrolled_courses():
    courses = dao.get_enrolled_courses_by_user(current_user.id)
    course_list = []
    for c in courses:
        prog = dao.get_user_course_progress(current_user.id, c.id)
        course_list.append({
            'data': c,
            'progress': prog
        })
    return render_template('my_enrolled_courses.html', courses=course_list)


@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = dao.get_course_by_id(course_id)
    if not course or not course.is_active:
        flash("Khóa học không tồn tại hoặc đã bị xóa!", "error")
        return redirect('/')

    is_owner = False
    is_enrolled = False
    progress = 0
    completed_test_ids = set()
    user_rating = None

    if current_user.is_authenticated:
        is_owner = dao.is_course_owner(current_user, course)
        is_enrolled = bool(dao.check_enrollment(current_user.id, course.id))

        if is_enrolled:
            progress = dao.get_user_course_progress(current_user.id, course_id)
            completed_test_ids = dao.get_user_completed_test_ids(current_user.id, course_id)
            user_rating = dao.get_user_rating_for_course(current_user.id, course_id)
        elif is_owner:
            progress = 100

    rating_stats = dao.get_course_rating_stats(course_id)
    ratings = dao.get_course_ratings(course_id)

    return render_template(
        'course_detail.html',
        course=course,
        is_owner=is_owner,
        is_enrolled=is_enrolled,
        progress=progress,
        completed_test_ids=completed_test_ids,
        rating_stats=rating_stats,
        ratings=ratings,
        user_rating=user_rating
    )


@app.route('/courses/<int:course_id>/rate', methods=['POST'])
def rate_course(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    if current_user.role != UserRole.STUDENT:
        flash("Chỉ học viên mới có quyền đánh giá khóa học!", "error")
        return redirect(f'/courses/{course_id}')

    raw_rating = request.form.get('rating')
    comment = request.form.get('comment', '').strip()

    if not raw_rating or not str(raw_rating).isdigit() or not (1 <= int(raw_rating) <= 5):
        flash("Vui lòng chọn mức đánh giá hợp lệ (từ 1 đến 5 sao)!", "error")
        return redirect(f'/courses/{course_id}')

    rating_value = int(raw_rating)
    rating, err = dao.add_or_update_rating(current_user.id, course_id, rating_value, comment)

    if err:
        flash(err, "error")
    else:
        flash("Đã lưu đánh giá của bạn thành công!", "success")

    return redirect(f'/courses/{course_id}')


@app.route('/courses/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != UserRole.TEACHER:
        flash("Chỉ giảng viên mới có quyền tạo khóa học!", "error")
        return redirect('/')

    categories = dao.get_categories()
    tags = dao.get_all_tags()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = request.form.get('price', 0)
        category_id = request.form.get('category_id')
        description = request.form.get('description', '').strip()
        selected_tag_ids = request.form.getlist('tag_ids')

        if not selected_tag_ids:
            return render_template('create_course.html', categories=categories, tags=tags,
                                   err_msg="Vui lòng chọn ít nhất một thẻ Tag cho khóa học!")

        if not name or not category_id:
            return render_template('create_course.html', categories=categories, tags=tags,
                                   err_msg="Vui lòng nhập đầy đủ tên khóa học và thể loại!")

        img_drive_id = DEFAULT_COURSE_IMG_DRIVE_ID
        img_url = DEFAULT_COURSE_IMG_URL

        img = request.files.get("img")
        if img and img.filename and img.filename.strip() != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            uploaded_id, uploaded_url = upload_file(filepath, filename)

            if os.path.exists(filepath):
                os.remove(filepath)

            if uploaded_id is None:
                return render_template('create_course.html', categories=categories, tags=tags,
                                       err_msg="Tải ảnh bìa khóa học lên Cloudinary thất bại! Vui lòng thử lại.")

            img_drive_id = uploaded_id
            img_url = uploaded_url

        try:
            new_course = dao.create_course(
                name=name,
                price=price,
                category_id=category_id,
                description=description,
                teacher_id=current_user.id,
                img_drive_id=img_drive_id,
                img_url=img_url,
                tag_ids=selected_tag_ids
            )
            flash("Tạo khóa học thành công!", "success")
            return redirect(url_for('course_detail', course_id=new_course.id))
        except Exception as ex:
            print("Lỗi tạo khóa học:", ex)
            return render_template('create_course.html', categories=categories, tags=tags,
                                   err_msg="Có lỗi xảy ra khi tạo khóa học!")

    return render_template('create_course.html', categories=categories, tags=tags)


@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def update_course(course_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    err_msg = ""
    course = dao.get_course_by_id(course_id)
    if course is None:
        err_msg = "Khóa học không tồn tại"
        return render_template("my_courses.html", err_msg=err_msg)

    if not dao.is_course_owner(current_user, course):
        err_msg = "Bạn không có quyền chỉnh sửa khóa học này"
        return render_template("home.html", err_msg=err_msg)

    categories = dao.get_categories()
    tags = dao.get_all_tags()
    current_tag_ids = [ct.tag_id for ct in course.course_tags]

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        selected_tag_ids = request.form.getlist('tag_ids')

        img_drive_id = course.img_drive_id
        img_url = course.img_url

        img = request.files.get("img")
        if img and img.filename != '':
            os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)

            uploaded_id, uploaded_url = upload_file(filepath, filename)
            os.remove(filepath)

            if uploaded_id is None:
                err_msg = "Tải ảnh lên hệ thống thất bại, vui lòng thử lại."
                return render_template(
                    "create_course.html",
                    course=course,
                    categories=categories,
                    tags=tags,
                    current_tag_ids=current_tag_ids,
                    err_msg=err_msg
                )

            img_drive_id = uploaded_id
            img_url = f"https://lh3.googleusercontent.com/d/{uploaded_id}"

        if not name or not category_id:
            err_msg = "Vui lòng nhập tên khóa học và chọn danh mục!"
            return render_template(
                'create_course.html',
                course=course,
                categories=categories,
                tags=tags,
                current_tag_ids=current_tag_ids,
                err_msg=err_msg
            )

        if not selected_tag_ids:
            err_msg = "Vui lòng chọn ít nhất một thẻ Tag cho khóa học!"
            return render_template(
                'create_course.html',
                course=course,
                categories=categories,
                tags=tags,
                current_tag_ids=current_tag_ids,
                err_msg=err_msg
            )

        try:
            dao.update_course(
                course=course,
                name=name,
                price=price,
                category_id=category_id,
                description=description,
                img_drive_id=img_drive_id,
                img_url=img_url,
                tag_ids=selected_tag_ids
            )
            return redirect(f'/courses/{course.id}')
        except Exception as ex:
            db.session.rollback()
            print(ex)
            err_msg = "Có lỗi xảy ra khi cập nhật khóa học. Vui lòng thử lại sau!"
            return render_template(
                'create_course.html',
                course=course,
                categories=categories,
                tags=tags,
                current_tag_ids=current_tag_ids,
                err_msg=err_msg
            )

    return render_template(
        'create_course.html',
        course=course,
        categories=categories,
        tags=tags,
        current_tag_ids=current_tag_ids,
        err_msg=err_msg
    )


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
    if not course or not current_user.is_authenticated or not dao.is_course_owner(current_user, course):
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name or not name.strip():
            return render_template("create_chapter.html", course=course, err_msg="Bạn phải đặt tên cho chương!")

        chapter = Chapter(
            name=name.strip(),
            description=description.strip() if description else None,
            course_id=course_id,
            is_active=True
        )

        try:
            db.session.add(chapter)
            db.session.commit()
            flash("Tạo chương mới thành công!", "success")
            return redirect(f"/courses/{course_id}")
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template("create_chapter.html", course=course, err_msg=f"Lỗi: {ex}")

    return render_template("create_chapter.html", course=course)


@app.route('/courses/<int:course_id>/chapters/<int:chapter_id>/update', methods=["GET", "POST"])
def update_chapters(course_id, chapter_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    course = dao.get_course_by_id(course_id)
    if not course or not dao.is_course_owner(current_user, course):
        return redirect("/")

    chapter = dao.get_chapter_by_id(chapter_id)
    if not chapter or chapter.course_id != course_id or not chapter.is_active:
        flash("Chương này không tồn tại hoặc đã bị xóa!", "error")
        return redirect(f"/courses/{course_id}")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name or not name.strip():
            return render_template("create_chapter.html", course=course, chapter=chapter, err_msg="Tên chương không được để trống!")

        try:
            chapter.name = name.strip()
            chapter.description = description.strip() if description else None
            db.session.commit()
            flash("Cập nhật chương thành công!", "success")
            return redirect(f"/courses/{course_id}")
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template("create_chapter.html", course=course, chapter=chapter, err_msg=f"Lỗi: {ex}")

    return render_template("create_chapter.html", course=course, chapter=chapter)


@app.route('/courses/<int:course_id>/chapters/<int:chapter_id>/delete', methods=["POST"])
def delete_chapter(course_id, chapter_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    course = dao.get_course_by_id(course_id)
    if not course or not dao.is_course_owner(current_user, course):
        return redirect("/")

    chapter = dao.get_chapter_by_id(chapter_id)
    if not chapter or chapter.course_id != course_id:
        flash("Chương không tồn tại!", "error")
        return redirect(f"/courses/{course_id}")

    try:
        chapter.is_active = False

        for lesson in chapter.lessons:
            lesson.is_active = False

        for test in chapter.tests:
            test.is_active = False

        db.session.commit()
        flash(f"Đã xóa mềm chương '{chapter.name}' thành công!", "success")
    except Exception as ex:
        db.session.rollback()
        print(ex)
        flash(f"Lỗi khi xóa chương: {ex}", "error")

    return redirect(f"/courses/{course_id}")


@app.route('/chapters/<int:chapter_id>/lessons')
@login_required
def lessons(chapter_id):
    chapter = dao.get_chapter_by_id(chapter_id)
    if not chapter or not chapter.is_active:
        flash("Chương không tồn tại hoặc đã bị xóa!", "error")
        return redirect(url_for('get_all_courses'))

    course = chapter.course
    is_owner = dao.is_course_owner(current_user, course)
    is_enrolled = dao.check_enrollment(current_user.id, course.id)

    if not is_owner and not is_enrolled:
        flash("Cảnh báo: Bạn cần đăng ký khóa học để xem nội dung bài giảng này!", "error")
        return redirect(url_for('course_detail', course_id=course.id))

    active_lessons = [l for l in chapter.lessons if l.is_active]

    return render_template('lesson.html', chapter=chapter, course=course, is_owner=is_owner, lessons=active_lessons)


@app.route("/chapters/<int:chapter_id>/lessons/add", methods=["GET", "POST"])
@app.route("/lessons/<int:lesson_id>/update", methods=["GET", "POST"])
def create_or_update_lesson(chapter_id=None, lesson_id=None):
    lesson = None

    if lesson_id:
        lesson = dao.get_lesson_by_id(lesson_id)
        if lesson is None or not lesson.is_active:
            flash("Bài giảng không tồn tại hoặc đã bị xóa!", "error")
            return redirect("/")
        if not current_user.is_authenticated or not dao.is_lesson_owner(current_user, lesson):
            flash("Bạn không có quyền chỉnh sửa bài giảng này!", "error")
            return redirect("/")
        chapter = lesson.chapter
        course = chapter.course
    else:
        chapter = dao.get_chapter_by_id(chapter_id)
        if not chapter or not chapter.is_active or not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
            flash("Chương không hợp lệ hoặc bạn không có quyền thêm bài giảng!", "error")
            return redirect("/")
        course = chapter.course

    if request.method == "POST":
        title = request.form.get("title")
        article = request.form.get("article", "")

        if not title or not title.strip():
            return render_template(
                "create_lesson.html",
                chapter=chapter,
                course=course,
                lesson=lesson,
                err_msg="Vui lòng nhập tiêu đề cho bài giảng!"
            )

        os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

        video_drive_id = lesson.video_drive_id if lesson else None
        video_url = lesson.video_url if lesson else None
        old_video_drive_id = video_drive_id
        video_replaced = False

        video = request.files.get("video")
        if video and video.filename and video.filename.strip() != '':
            filename = secure_filename(video.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            video.save(filepath)

            if os.path.getsize(filepath) > 0:
                try:
                    uploaded_id, uploaded_url = upload_file(filepath, filename)
                except Exception as upload_err:
                    print("Lỗi khi gọi upload_file Drive:", upload_err)
                    uploaded_id, uploaded_url = None, None

                if os.path.exists(filepath):
                    os.remove(filepath)

                if uploaded_id is None:
                    return render_template(
                        "create_lesson.html",
                        chapter=chapter, course=course, lesson=lesson,
                        err_msg="Tải video lên Google Drive thất bại! Hãy kiểm tra token xác thực hoặc dung lượng file."
                    )

                video_drive_id, video_url = uploaded_id, uploaded_url
                video_replaced = True
            else:
                if os.path.exists(filepath):
                    os.remove(filepath)

        file_drive_id = lesson.file_drive_id if lesson else None
        file_url = lesson.file_url if lesson else None
        old_file_drive_id = file_drive_id
        file_replaced = False

        pdf_file = request.files.get("pdf")
        if pdf_file and pdf_file.filename != '':
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            pdf_file.save(filepath)
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

            if uploaded_id is None:
                return render_template(
                    "create_lesson.html",
                    chapter=chapter, course=course, lesson=lesson,
                    err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại."
                )

            img_drive_id = uploaded_id
            img_url = f"https://lh3.googleusercontent.com/d/{uploaded_id}"
            img_replaced = True

        img_drive_id = lesson.img_drive_id if lesson else DEFAULT_LESSON_IMG_DRIVE_ID
        img_url = lesson.img_url if lesson else DEFAULT_LESSON_IMG_URL
        old_img_drive_id = img_drive_id
        img_replaced = False

        img = request.files.get("img")
        if img and img.filename != '':
            filename = secure_filename(img.filename)
            filepath = os.path.join(TEMP_UPLOAD_DIR, filename)
            img.save(filepath)
            uploaded_id, uploaded_url = upload_file(filepath, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

            if uploaded_id is None:
                return render_template(
                    "create_lesson.html",
                    chapter=chapter, course=course, lesson=lesson,
                    err_msg="Tải ảnh lên hệ thống thất bại, vui lòng thử lại."
                )

            img_drive_id, img_url = uploaded_id, uploaded_url
            img_replaced = True

        if lesson:
            lesson.title = title.strip()
            lesson.article = article
            lesson.video_drive_id = video_drive_id
            lesson.video_url = video_url
            lesson.file_drive_id = file_drive_id
            lesson.file_url = file_url
            lesson.img_drive_id = img_drive_id
            lesson.img_url = img_url
        else:
            lesson = Lesson(
                chapter_id=chapter.id,
                title=title.strip(),
                article=article,
                video_drive_id=video_drive_id,
                video_url=video_url,
                file_drive_id=file_drive_id,
                file_url=file_url,
                img_drive_id=img_drive_id,
                img_url=img_url,
                is_active=True
            )
            db.session.add(lesson)

        try:
            db.session.commit()
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template(
                "create_lesson.html",
                chapter=chapter, course=course, lesson=lesson,
                err_msg="Lưu bài học thất bại, vui lòng thử lại."
            )

        if lesson_id:
            if video_replaced and old_video_drive_id:
                try:
                    delete_file(old_video_drive_id)
                except Exception as ex:
                    print("Không xóa được video cũ:", ex)
            if file_replaced and old_file_drive_id:
                try:
                    delete_file(old_file_drive_id)
                except Exception as ex:
                    print("Không xóa được PDF cũ:", ex)
            if img_replaced and old_img_drive_id and old_img_drive_id != DEFAULT_LESSON_IMG_DRIVE_ID:
                try:
                    delete_file(old_img_drive_id)
                except Exception as ex:
                    print("Không xóa được ảnh cũ:", ex)

        flash("Lưu bài giảng thành công!", "success")
        return redirect(f"/lessons/{lesson.id}/detail")

    return render_template(
        "create_lesson.html",
        chapter=chapter,
        course=course,
        lesson=lesson
    )


@app.route("/lessons/<int:lesson_id>/delete", methods=["POST"])
def delete_lesson(lesson_id):
    lesson = dao.get_lesson_by_id(lesson_id)
    if not lesson:
        flash("Bài học không tồn tại!", "error")
        return redirect('/')

    chapter = lesson.chapter
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        flash("Bạn không có quyền xóa bài học này!", "error")
        return redirect(f"/chapters/{chapter.id}/lessons")

    try:
        lesson.is_active = False
        db.session.commit()
        flash(f"Đã xóa bài học '{lesson.title}' thành công!", "success")
    except Exception as ex:
        db.session.rollback()
        print(ex)
        flash(f"Lỗi khi xóa bài học: {ex}", "error")

    return redirect(f"/chapters/{chapter.id}/lessons")


@app.route("/lessons/<int:lesson_id>/detail")
@login_required
def lesson_detail(lesson_id):
    lesson = dao.get_lesson_by_id(lesson_id)
    if not lesson or not lesson.is_active:
        flash("Bài giảng không tồn tại hoặc đã bị xóa!", "error")
        return redirect('/')

    chapter = lesson.chapter
    course = chapter.course
    is_owner = dao.is_course_owner(current_user, course)
    is_enrolled = dao.check_enrollment(current_user.id, course.id)

    if not is_owner and not is_enrolled:
        flash("Bạn cần đăng ký khóa học để xem nội dung bài giảng này!", "error")
        return redirect(url_for('course_detail', course_id=course.id))

    active_lessons = [l for l in chapter.lessons if l.is_active]

    current_index = 0
    for idx, l in enumerate(active_lessons):
        if l.id == lesson.id:
            current_index = idx
            break

    prev_lesson = active_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = active_lessons[current_index + 1] if current_index < len(active_lessons) - 1 else None

    return render_template(
        "lesson_detail.html",
        lesson=lesson,
        chapter=chapter,
        course=course,
        is_owner=is_owner,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson
    )


@app.route("/media/video/<file_id>")
def stream_video(file_id):
    # Redirect trực tiếp sang URL Cloudinary tương ứng
    lesson = Lesson.query.filter_by(video_drive_id=file_id).first()
    if lesson and lesson.video_url:
        return redirect(lesson.video_url)
    return "Video not found", 404


# ---------------- AI CHAT ROUTES ----------------

@app.route("/ai_chat")
@app.route("/ai_chat/new")
def ai_chat_page():
    if not current_user.is_authenticated:
        return redirect("/login")
    return render_template("ai_chat.html")


@app.route("/ai_chat/rooms", methods=["GET"])
def list_ai_chat_rooms():
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    rooms = (
        AIChatRoom.query.filter_by(user_id=current_user.id)
        .order_by(AIChatRoom.updated_date.desc())
        .all()
    )
    return jsonify(
        [
            {
                "id": r.id,
                "title": r.title,
                "updated_date": r.updated_date.isoformat() if r.updated_date else None,
            }
            for r in rooms
        ]
    )


@app.route("/ai_chat/rooms", methods=["POST"])
def create_ai_chat_room():
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    room = AIChatRoom(user_id=current_user.id, title="Cuộc trò chuyện mới")
    db.session.add(room)
    db.session.commit()
    return jsonify({"id": room.id, "title": room.title})


@app.route("/ai_chat/rooms/<int:room_id>", methods=["DELETE"])
def delete_ai_chat_room(room_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    room = AIChatRoom.query.get(room_id)
    if not room or room.user_id != current_user.id:
        return jsonify({"error": "Không tìm thấy cuộc trò chuyện"}), 404

    db.session.delete(room)
    db.session.commit()
    return jsonify({"status": "ok"})


@app.route("/ai_chat/rooms/<int:room_id>/messages", methods=["GET"])
def get_ai_chat_messages(room_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    room = AIChatRoom.query.get(room_id)
    if not room or room.user_id != current_user.id:
        return jsonify({"error": "Không tìm thấy cuộc trò chuyện"}), 404

    messages = (
        AIChatRoomMessage.query.filter_by(ai_chat_room_id=room_id)
        .order_by(AIChatRoomMessage.id.asc())
        .all()
    )
    return jsonify(
        {
            "title": room.title,
            "messages": [_serialize_message(m) for m in messages],
        }
    )


@app.route("/ai_chat/rooms/<int:room_id>/messages", methods=["POST"])
def send_ai_chat_message(room_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    room = AIChatRoom.query.get(room_id)
    if not room or room.user_id != current_user.id:
        return jsonify({"error": "Không tìm thấy cuộc trò chuyện"}), 404

    data = request.get_json(force=True)
    user_message = (data or {}).get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Tin nhắn rỗng"}), 400
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({
            "error": f"Tin nhắn quá dài (tối đa {MAX_MESSAGE_LENGTH} ký tự)"
        }), 400

    user_msg = AIChatRoomMessage(
        ai_chat_room_id=room_id,
        user_id=current_user.id,
        sender_type=SenderType.USER,
        content=user_message,
    )
    db.session.add(user_msg)
    db.session.commit()

    history_rows = (
        AIChatRoomMessage.query.filter_by(ai_chat_room_id=room_id)
        .order_by(AIChatRoomMessage.id.asc())
        .all()
    )
    history_rows = history_rows[-MAX_TURNS_SENT:]

    contents = [
        {
            "role": "user" if m.sender_type == SenderType.USER else "model",
            "parts": [{"text": m.content}],
        }
        for m in history_rows
    ]

    system_instruction = (
        SYSTEM_INSTRUCTION
        + "\n\nDanh sách khóa học hiện có (chỉ được điền course_ids nằm trong danh sách này):\n"
        + _build_courses_context()
        + "\n\nLuôn trả lời đúng theo JSON schema được cung cấp."
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA,
            ),
        )
        result = json.loads(response.text)
        reply_text = (result.get("reply") or "").strip() or "Xin lỗi, mình chưa có câu trả lời phù hợp."
        course_ids = result.get("course_ids") or []
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi khi gọi Gemini API: {e}"}), 500

    ai_msg = AIChatRoomMessage(
        ai_chat_room_id=room_id,
        user_id=None,
        sender_type=SenderType.AI,
        content=reply_text,
    )
    db.session.add(ai_msg)
    db.session.flush()

    valid_courses = (
        Course.query.filter(Course.id.in_(course_ids)).all() if course_ids else []
    )
    for c in valid_courses:
        db.session.add(
            CourseRecommendation(
                user_id=current_user.id,
                course_id=c.id,
                ai_chat_room_message_id=ai_msg.id,
            )
        )

    if room.title == "Cuộc trò chuyện mới":
        room.title = user_message[:40] + ("..." if len(user_message) > 40 else "")

    room.updated_date = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify(
        {
            "reply": reply_text,
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "category": c.category.name if c.category else "",
                    "price": c.price or 0,
                    "icon": "📘",
                }
                for c in valid_courses
            ],
        }
    )


@app.route("/ai_chat/recommendations", methods=["GET"])
def get_ai_recommendations():
    if not current_user.is_authenticated:
        return jsonify({"error": "Chưa đăng nhập"}), 401

    courses = dao.get_recommended_courses_for_user(current_user.id)
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "category": c.category.name if c.category else "",
            "price": c.price or 0,
            "img_url": c.img_url,
        }
        for c in courses
    ])


# ---------------- SOCKET.IO & LIVE CHAT ROUTES ----------------

@socketio.on('join_chat')
def handle_join(data):
    room_id = str(data['room_id'])
    join_room(room_id)


@socketio.on('send_message')
def handle_send_message(data):
    room_id = data['room_id']
    content = data['content']
    sender_id = current_user.id

    msg = ChatRoomMessage(
        chat_room_id=room_id,
        sender_id=sender_id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()

    avatar_url = current_user.img_url if (current_user.img_url and str(current_user.img_url).strip() != "") else ""
    avatar_text = current_user.name[0].upper() if (current_user.name and len(current_user.name) > 0) else "U"

    emit('receive_message', {
        'sender_id': sender_id,
        'sender_name': current_user.name,
        'avatar_url': avatar_url,
        'avatar_text': avatar_text,
        'content': content
    }, room=str(room_id))


@app.route('/courses/<int:course_id>/chat')
def join_course_chat(course_id):
    course = dao.get_course_by_id(course_id)
    if not course:
        flash("Khóa học không tồn tại!", "error")
        return redirect(url_for('home'))

    if current_user.id == course.teacher_id:
        student_rooms = dao.get_teacher_chat_rooms(course.id, current_user.id)
        if student_rooms:
            return redirect(url_for('open_chat_room', room_id=student_rooms[0].id))
        else:
            err_msg = "Hiện chưa có học viên nào tham gia phòng hỏi đáp của khóa học này!"
            return render_template('course_detail.html', course=course, progress=35, err_msg=err_msg)

    room = dao.get_or_create_chat_room(
        student_id=current_user.id,
        teacher_id=course.teacher_id,
        course_id=course.id
    )
    return redirect(url_for('open_chat_room', room_id=room.id))


@app.route('/chat/<int:room_id>')
def open_chat_room(room_id):
    room = dao.get_chat_room_by_id(room_id)
    if not room:
        flash("Phòng trò chuyện không tồn tại hoặc đã bị xóa!", "error")
        return redirect(url_for('home'))

    if current_user.id not in [room.student_id, room.teacher_id]:
        flash("Cảnh báo: Bạn không có quyền truy cập vào phòng trò chuyện của người khác!", "error")
        return redirect(url_for('course_detail', course_id=room.course_id))

    messages = dao.get_chat_messages(room.id)

    student_rooms = []
    if current_user.id == room.teacher_id:
        student_rooms = dao.get_teacher_chat_rooms(room.course_id, current_user.id)

    return render_template(
        'chat_room.html',
        room=room,
        course=room.course,
        messages=messages,
        student_rooms=student_rooms
    )


# ---------------- THANH TOÁN VNPAY ----------------

@app.route('/checkout/<int:course_id>')
@login_required
def checkout(course_id):
    course = dao.get_course_by_id(course_id)
    if not course:
        flash("Không tìm thấy thông tin khóa học để thanh toán!", "error")
        return redirect(url_for('get_all_courses'))

    if dao.check_enrollment(current_user.id, course.id):
        flash("Bạn đã đăng ký khóa học này rồi!", "info")
        return redirect(url_for('course_detail', course_id=course.id))

    return render_template('checkout.html', course=course)


@app.route('/checkout/<int:course_id>/process', methods=['POST'])
@login_required
def process_checkout(course_id):
    course = dao.get_course_by_id(course_id)
    if not course:
        flash("Không tìm thấy thông tin khóa học!", "error")
        return redirect(url_for('get_all_courses'))

    if not course.price or course.price <= 0:
        dao.enroll_course(current_user.id, course.id)
        flash("Đăng ký khóa học miễn phí thành công!", "success")
        return redirect(url_for('course_detail', course_id=course.id))

    # Lấy thông tin cấu hình từ biến môi trường (fallback trực tiếp nếu VNPAY_CONFIG bị thiếu)
    tmn_code = VNPAY_CONFIG.get('vnp_TmnCode') or os.getenv('VNPAY_TMN_CODE')
    hash_secret = VNPAY_CONFIG.get('vnp_HashSecret') or os.getenv('VNPAY_HASH_SECRET')
    vnpay_url = VNPAY_CONFIG.get('vnp_Url') or os.getenv('VNPAY_URL')
    return_url = VNPAY_CONFIG.get('vnp_ReturnUrl') or os.getenv('VNPAY_RETURN_URL')

    if not hash_secret or not tmn_code:
        flash("Lỗi hệ thống: Chưa cấu hình thông tin VNPAY Sandbox!", "error")
        return redirect(url_for('checkout', course_id=course.id))

    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = tmn_code
    vnp.requestData['vnp_Amount'] = str(int(course.price) * 100)
    vnp.requestData['vnp_CurrCode'] = 'VND'

    txn_ref = f"{current_user.id}-{course.id}-{int(datetime.now().timestamp())}"
    vnp.requestData['vnp_TxnRef'] = txn_ref
    vnp.requestData['vnp_OrderInfo'] = f"Thanh toan khoa hoc {course.name}"
    vnp.requestData['vnp_OrderType'] = 'billpayment'
    vnp.requestData['vnp_Locale'] = 'vn'
    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp.requestData['vnp_IpAddr'] = request.remote_addr or '127.0.0.1'
    vnp.requestData['vnp_ReturnUrl'] = return_url

    vnpay_payment_url = vnp.get_payment_url(vnpay_url, hash_secret)
    return redirect(vnpay_payment_url)


@app.route('/payment/vnpay_return')
def vnpay_return():
    vnp = vnpay()
    vnp.responseData = request.args.to_dict()

    if vnp.validate_response(VNPAY_CONFIG['vnp_HashSecret']):
        if vnp.responseData['vnp_ResponseCode'] == '00':
            txn_ref = vnp.responseData['vnp_TxnRef']
            user_id, course_id, _ = txn_ref.split('-')
            amount = int(vnp.responseData['vnp_Amount']) / 100

            if not dao.check_enrollment(user_id, course_id):
                dao.save_payment_history(user_id, course_id, txn_ref, amount)
                dao.enroll_course(user_id, course_id)

            flash("Thanh toán thành công! Chào mừng bạn đến với khóa học.", "success")
            return redirect(url_for('course_detail', course_id=course_id))
        else:
            flash("Thanh toán bị hủy hoặc không thành công!", "error")
            return redirect(url_for('home'))
    else:
        flash("Lỗi bảo mật: Dữ liệu thanh toán không hợp lệ!", "error")
        return redirect(url_for('home'))


# ---------------- CÁC ROUTE BÀI THI ----------------

@app.route('/chapters/<int:chapter_id>/tests')
def test_list(chapter_id):
    chapter = dao.get_chapter_by_id(chapter_id)
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")

    test = chapter.test if (chapter.test and chapter.test.is_active) else None
    return render_template("test_list.html", test=test, chapter_id=chapter_id)


@app.route('/tests/<int:test_id>')
def test_detail(test_id):
    test = Test.query.get(test_id)
    if not test or not test.is_active:
        return redirect('/')

    chapter = test.chapter
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")

    return render_template("test_detail.html", test=test)


@app.route('/tests/<int:test_id>/take', methods=['GET', 'POST'])
def take_test(test_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    test = Test.query.get(test_id)
    if not test or not test.is_active:
        return redirect('/')

    latest_result = (
        UserTest.query
        .filter_by(user_id=current_user.id, test_id=test.id)
        .order_by(UserTest.id.desc())
        .first()
    )

    if request.method == 'POST':
        questions = test.questions
        total_questions = len(questions)
        correct_count = 0

        for q in questions:
            selected_choice_id = request.form.get(f'question_{q.id}')
            if selected_choice_id:
                choice = Choice.query.get(int(selected_choice_id))
                if choice and choice.is_true:
                    correct_count += 1

        max_score = test.total_score or 10.0
        final_score = round((correct_count / total_questions) * max_score, 2) if total_questions > 0 else 0.0

        user_test = UserTest(
            user_id=current_user.id,
            test_id=test.id,
            score=final_score
        )
        db.session.add(user_test)

        try:
            db.session.commit()

            new_cert = None
            if test.chapter and test.chapter.course_id:
                new_cert = dao.check_and_issue_certificate(current_user.id, test.chapter.course_id)
                if new_cert:
                    flash("🎉 Chúc mừng! Bạn đã hoàn thành xuất sắc tất cả bài thi với điểm tuyệt đối và nhận được Chứng Chỉ Khóa Học!", "success")

            return render_template(
                'test_result.html',
                test=test,
                score=final_score,
                max_score=max_score,
                correct_count=correct_count,
                total_questions=total_questions,
                new_cert=new_cert
            )
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template(
                'take_test.html',
                test=test,
                previous_result=latest_result,
                err_msg="Có lỗi xảy ra khi nộp bài thi!"
            )

    return render_template('take_test.html', test=test, previous_result=latest_result)


@app.route("/courses/<int:course_id>/tests/add", methods=["GET", "POST"])
def add_test(course_id):
    course = dao.get_course_by_id(course_id)
    if not course or not current_user.is_authenticated or not dao.is_course_owner(current_user, course):
        return redirect("/")

    chapters = course.chapters

    if request.method == "POST":
        test_name = request.form.get("test_name")
        description = request.form.get("description", "")
        total_score = request.form.get("total_score", 10, type=float)
        chapter_id = request.form.get("chapter_id", type=int)

        if not test_name or not test_name.strip():
            return render_template("create_test.html", course=course, chapters=chapters, err_msg="Vui lòng nhập tên bài thi!")

        if not chapter_id:
            return render_template("create_test.html", course=course, chapters=chapters, err_msg="Vui lòng chọn chương cho bài thi!")

        active_test = Test.query.filter_by(chapter_id=chapter_id, is_active=True).first()
        if active_test:
            return render_template(
                "create_test.html",
                course=course,
                chapters=chapters,
                err_msg=f"Chương '{active_test.chapter.name}' hiện đã có bài thi đang hoạt động ('{active_test.name}'). Vui lòng xóa bài thi cũ trước hoặc chọn chương khác!"
            )

        try:
            new_test = Test(
                name=test_name.strip(),
                description=description.strip() if description else None,
                chapter_id=chapter_id,
                total_score=total_score,
                is_active=True
            )
            db.session.add(new_test)
            db.session.flush()

            question_contents = request.form.getlist("question_content[]")
            for index, content in enumerate(question_contents):
                if content and content.strip():
                    question = Question(test_id=new_test.id, content=content.strip())
                    db.session.add(question)
                    db.session.flush()

                    choices = request.form.getlist(f"choice_answer_{index}[]")
                    correct_choice_idx = request.form.get(f"correct_choice_{index}")

                    for c_idx, choice_text in enumerate(choices):
                        if choice_text and choice_text.strip():
                            is_true = (str(c_idx) == str(correct_choice_idx))
                            choice = Choice(
                                question_id=question.id,
                                answer=choice_text.strip(),
                                is_true=is_true
                            )
                            db.session.add(choice)

            db.session.commit()
            flash("Tạo bài thi mới thành công!", "success")
            return redirect(f"/courses/{course_id}")

        except Exception as ex:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return render_template("create_test.html", course=course, chapters=chapters, err_msg=f"Có lỗi xảy ra: {ex}")

    return render_template("create_test.html", course=course, chapters=chapters)


@app.route('/tests/<int:test_id>/delete', methods=['POST'])
def delete_test(test_id):
    test = Test.query.get(test_id)
    if not test:
        flash("Bài thi không tồn tại!", "error")
        return redirect('/')

    course_id = test.chapter.course_id
    if not current_user.is_authenticated or not dao.is_course_owner(current_user, test.chapter.course):
        flash("Bạn không có quyền xóa bài thi này!", "error")
        return redirect(f"/courses/{course_id}")

    try:
        test.is_active = False
        db.session.commit()
        flash("Đã xóa bài thi thành công (đưa vào trạng thái ngưng hoạt động)!", "success")
    except Exception as ex:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        flash(f"Lỗi khi xóa bài thi: {ex}", "error")

    return redirect(f"/courses/{course_id}")


@app.route('/tests/<int:test_id>/clone', methods=['GET', 'POST'])
def clone_test(test_id):
    source_test = Test.query.get(test_id)
    if not source_test:
        return redirect('/')

    course = source_test.chapter.course
    if not current_user.is_authenticated or not dao.is_course_owner(current_user, course):
        return redirect("/")

    chapters = course.chapters

    if request.method == "POST":
        test_name = request.form.get("test_name")
        description = request.form.get("description", "")
        total_score = request.form.get("total_score", 10, type=float)
        target_chapter_id = request.form.get("chapter_id", type=int)

        if not test_name or not test_name.strip():
            return render_template("create_test.html", course=course, chapters=chapters, source_test=source_test, err_msg="Vui lòng nhập tên bài thi!")

        if not target_chapter_id:
            return render_template("create_test.html", course=course, chapters=chapters, source_test=source_test, err_msg="Vui lòng chọn chương cho bài thi clone!")

        active_test = Test.query.filter_by(chapter_id=target_chapter_id, is_active=True).first()
        if active_test:
            return render_template(
                "create_test.html",
                course=course,
                chapters=chapters,
                source_test=source_test,
                err_msg=f"Chương '{active_test.chapter.name}' đã có bài thi đang hoạt động ('{active_test.name}'). Vui lòng xóa bài thi của chương đó trước hoặc chọn chương khác!"
            )

        try:
            new_test = Test(
                name=test_name.strip(),
                description=description.strip() if description else None,
                chapter_id=target_chapter_id,
                total_score=total_score,
                is_active=True
            )
            db.session.add(new_test)
            db.session.flush()

            question_contents = request.form.getlist("question_content[]")
            for index, content in enumerate(question_contents):
                if content and content.strip():
                    question = Question(test_id=new_test.id, content=content.strip())
                    db.session.add(question)
                    db.session.flush()

                    choices = request.form.getlist(f"choice_answer_{index}[]")
                    correct_choice_idx = request.form.get(f"correct_choice_{index}")

                    for c_idx, choice_text in enumerate(choices):
                        if choice_text and choice_text.strip():
                            is_true = (str(c_idx) == str(correct_choice_idx))
                            choice = Choice(
                                question_id=question.id,
                                answer=choice_text.strip(),
                                is_true=is_true
                            )
                            db.session.add(choice)

            db.session.commit()
            flash("Nhân bản bài thi thành công!", "success")
            return redirect(f"/courses/{course.id}")

        except Exception as ex:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return render_template("create_test.html", course=course, chapters=chapters, source_test=source_test, err_msg=f"Có lỗi: {ex}")

    return render_template("create_test.html", course=course, chapters=chapters, source_test=source_test)


# ---------------- CẤP CHỨNG CHỈ ----------------

@app.route('/my_certificates')
@login_required
def my_certificates():
    certs = dao.get_user_certificates(current_user.id)
    return render_template('my_certificates.html', certs=certs)


@app.route('/certificates/<string:cert_code>')
@login_required
def view_certificate(cert_code):
    cert = dao.get_certificate_by_code(cert_code)
    if not cert:
        flash("Chứng chỉ không tồn tại hoặc đã bị thu hồi!", "error")
        return redirect('/')

    is_owner = dao.is_course_owner(current_user, cert.course)
    if cert.user_id != current_user.id and not is_owner:
        flash("Bạn không có quyền truy cập chứng chỉ này!", "error")
        return redirect('/')

    return render_template('certificate_view.html', cert=cert)


# ---------------- THỐNG KÊ GIẢNG VIÊN ----------------

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != UserRole.TEACHER:
        flash("Bạn không có quyền truy cập trang quản trị của Giảng viên!", "error")
        return redirect('/')

    stats = dao.get_teacher_dashboard_stats(current_user.id)
    courses = dao.get_teacher_course_performance(current_user.id)
    chart_data = dao.get_teacher_revenue_chart(current_user.id)

    return render_template(
        'teacher_dashboard.html',
        stats=stats,
        courses=courses,
        chart_data=chart_data
    )


if __name__ == '__main__':
    socketio.run(app, debug=True)