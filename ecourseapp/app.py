import os
import requests
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect, Response, stream_with_context
from google.auth.transport.requests import Request as GoogleAuthRequest
from werkzeug.utils import secure_filename

from __init__ import app, db, login
from services.drive_service import upload_file, credentials
from models import User, UserRole, Level, Lesson, Chapter, Course, Question, Test, Choice, UserTest
import dao

import admin

TEMP_UPLOAD_DIR = "temp"


@app.route('/')
def home():
    kw = request.args.get('kw')
    category_id = request.args.get('category_id')

    courses = dao.get_courses(kw=kw, category_id=category_id)
    return render_template('home.html', courses=courses)


@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = dao.get_course_by_id(course_id)

    if not course:
        err_msg = "Không tìm thấy khóa học!"

    return render_template('course_detail.html', course=course, progress=35)



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

        if not name or not category_id:
            err_msg = "Vui lòng nhập tên khóa học và chọn danh mục!"
        else:
            try:
                new_course = dao.create_course(
                    name=name,
                    price=price,
                    category_id=category_id,
                    description=description,
                    user_id=current_user.id
                )
                return redirect(f'/courses/{new_course.id}')
            except Exception as ex:
                db.session.rollback()
                print(ex)
                err_msg = "Có lỗi xảy ra khi đăng khóa học. Vui lòng thử lại sau!"
    return render_template('create_course.html', categories=categories, err_msg=err_msg)


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
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm"]
        role = request.form["role"]

        if password != confirm:
            err_msg = "Xác nhận mật khẩu không khớp!"
            return render_template("register.html", err_msg=err_msg)
        else:
            existing_user = User.query.filter(User.email == email).first()
            if existing_user:
                err_msg = "Tài khoản này đã được đăng ký"
                return render_template("register.html", err_msg=err_msg)
            else:
                try:
                    password = generate_password_hash(password)
                    user = User(
                        name=name,
                        email=email,
                        password=password,
                        role=UserRole(role),
                    )
                    db.session.add(user)
                    db.session.commit()
                    return redirect('/login')
                except Exception as ex:
                    db.session.rollback()
                    print(ex)

                    err_msg = "Hệ thống đã bị lỗi! Xin vui lòng thử lại sau"
                    return render_template("register.html", err_msg=err_msg)
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


@app.route('/courses/<int:course_id>/chapters')
def chapters(course_id):
    course = dao.get_course_by_id(course_id)
    if not current_user.is_authenticated or not dao.is_course_owner(current_user, course):
        return redirect("/")
    chapter_list = db.session.query(Chapter).filter(Chapter.course_id == course_id).all()
    return render_template("chapter.html", chapters=chapter_list, course_id=course_id)


@app.route('/courses/<int:course_id>/chapters/add', methods=["GET", "POST"])
def add_chapters(course_id):
    course = dao.get_course_by_id(course_id)
    if not current_user.is_authenticated or not dao.is_course_owner(current_user, course):
        return redirect("/")

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        chapter = Chapter(
            name=name,
            description=description,
            course_id=course_id,
        )

        try:
            db.session.add(chapter)
            db.session.commit()
            return redirect(f"/courses/{course_id}/chapters")

        except Exception as ex:
            db.session.rollback()
            print(ex)
            return "Upload failed"

    chapter_list = db.session.query(Chapter).filter(Chapter.course_id == course_id).all()
    return render_template("create_chapter.html", chapters=chapter_list, course_id=course_id)


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

        lesson = Lesson(
            chapter_id=chapter_id,
            title=request.form["title"],
            video_drive_id=video_drive_id,
            video_url=video_url,
            file_drive_id=file_drive_id,
            file_url=file_url,
            article=request.form.get("article")
        )

        try:
            db.session.add(lesson)
            db.session.commit()
            return redirect(f"/courses/{chapter.course_id}/chapters")

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


@app.route('/chapters/<int:chapter_id>/tests')
def test_list(chapter_id):
    chapter = dao.get_chapter_by_id(chapter_id)
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")
    
    tests = Test.query.filter(Test.chapter_id == chapter_id, Test.is_active == True).all()
    return render_template("test_list.html", tests=tests, chapter_id=chapter_id)


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
            return render_template(
                'test_result.html',
                test=test,
                score=final_score,
                max_score=max_score,
                correct_count=correct_count,
                total_questions=total_questions
            )
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template('take_test.html', test=test, previous_result=latest_result, err_msg="Có lỗi xảy ra khi nộp bài thi!")

    return render_template('take_test.html', test=test, previous_result=latest_result)

@app.route("/chapters/<int:chapter_id>/tests/add", methods=["GET", "POST"])
def add_test(chapter_id):
    chapter = dao.get_chapter_by_id(chapter_id)
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")

    if request.method == "POST":
        test_name = request.form.get("test_name")
        description = request.form.get("description")
        total_score = request.form.get("total_score", 10, type=float)

        if not test_name:
            return render_template("create_test.html", chapter_id=chapter_id, err_msg="Vui lòng nhập tên bài thi!")

        try:
            new_test = Test(
                name=test_name,
                description=description,
                chapter_id=chapter_id,
                total_score=total_score
            )
            db.session.add(new_test)
            db.session.flush()
            
            question_contents = request.form.getlist("question_content[]")
            
            for index, content in enumerate(question_contents):
                if content.strip():
                    question = Question(test_id=new_test.id, content=content)
                    db.session.add(question)
                    db.session.flush()

                    choices = request.form.getlist(f"choice_answer_{index}[]")
                    correct_choice_idx = request.form.get(f"correct_choice_{index}")

                    for c_idx, choice_text in enumerate(choices):
                        if choice_text.strip():
                            is_true = (str(c_idx) == correct_choice_idx)
                            choice = Choice(
                                question_id=question.id,
                                answer=choice_text,
                                is_true=is_true
                            )
                            db.session.add(choice)

            db.session.commit()
            return redirect(f"/chapters/{chapter_id}/tests")

        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template("create_test.html", chapter_id=chapter_id, err_msg="Có lỗi xảy ra khi tạo bài thi!")

    return render_template("create_test.html", chapter_id=chapter_id)

@app.route('/tests/<int:test_id>/delete', methods=['POST'])
def delete_test(test_id):
    test = Test.query.get(test_id)
    if not test:
        return redirect('/')
    
    chapter = test.chapter
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")

    try:
        test.is_active = False  # Xóa mềm
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(ex)

    return redirect(f"/chapters/{chapter.id}/tests")

@app.route('/tests/<int:test_id>/clone', methods=['GET', 'POST'])
def clone_test(test_id):
    source_test = Test.query.get(test_id)
    if not source_test or not source_test.is_active:
        return redirect('/')

    chapter = source_test.chapter
    if not current_user.is_authenticated or not dao.is_chapter_owner(current_user, chapter):
        return redirect("/")

    if request.method == "POST":
        test_name = request.form.get("test_name")
        description = request.form.get("description")
        total_score = request.form.get("total_score", 10, type=float)

        if not test_name:
            return render_template("create_test.html", chapter_id=chapter.id, source_test=source_test, err_msg="Vui lòng nhập tên bài thi!")

        try:

            new_test = Test(
                name=test_name,
                description=description,
                chapter_id=chapter.id,
                total_score=total_score
            )
            db.session.add(new_test)
            db.session.flush()


            question_contents = request.form.getlist("question_content[]")
            for index, content in enumerate(question_contents):
                if content.strip():
                    question = Question(test_id=new_test.id, content=content)
                    db.session.add(question)
                    db.session.flush()

                    choices = request.form.getlist(f"choice_answer_{index}[]")
                    correct_choice_idx = request.form.get(f"correct_choice_{index}")

                    for c_idx, choice_text in enumerate(choices):
                        if choice_text.strip():
                            is_true = (str(c_idx) == correct_choice_idx)
                            choice = Choice(
                                question_id=question.id,
                                answer=choice_text,
                                is_true=is_true
                            )
                            db.session.add(choice)

            db.session.commit()
            return redirect(f"/chapters/{chapter.id}/tests")

        except Exception as ex:
            db.session.rollback()
            print(ex)
            return render_template("create_test.html", chapter_id=chapter.id, source_test=source_test, err_msg="Có lỗi xảy ra khi tạo bản sao bài thi!")


    return render_template("create_test.html", chapter_id=chapter.id, source_test=source_test)


if __name__ == '__main__':
    app.run(debug=True)
