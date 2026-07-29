import os
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect
from werkzeug.utils import secure_filename

from __init__ import app, db, login
from ecourseapp.services.drive_service import upload_file
from models import User, UserRole, Level, LessonContent, Lesson
import dao


@app.route('/')
def home():
    return render_template('home.html')


@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
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
            return redirect('/')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không đúng!"
            return render_template("login.html", err_msg=err_msg)

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():
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
                password = generate_password_hash(password)
                user = User(
                    name=name,
                    email=email,
                    password=password,
                    role=role,
                )
                try:
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
def logout():
    logout_user()
    return redirect('/')


@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect("/login")

    levels = list(Level)
    return render_template("profile.html", levels=levels)


@app.route('/profile/updateprofile', methods=["POST"])
def update_profile():
    if not current_user.is_authenticated:
        return redirect("/login")

    levels = list(Level)

    current_user.name = request.form["name"]
    current_user.level = Level(request.form["level"])
    current_user.major = request.form["major"]

    try:
        db.session.commit()
        return redirect('/profile')
    except Exception as ex:
        db.session.rollback()
        print(ex)

        err_msg = "Hệ thống đã bị lỗi! Xin vui lòng thử lại sau"
        return render_template("profile.html", levels=levels, err_msg=err_msg)


@app.route('/profile/updatepass', methods=["POST"])
def update_password():
    if not current_user.is_authenticated:
        return redirect("/login")

    oldpassword = request.form.get('oldpassword')
    newpassword = request.form.get("newpassword")
    confirm = request.form.get("confirm")

    if check_password_hash(current_user.password, oldpassword):
        if check_password_hash(current_user.password, newpassword):
            err_msg = "Mật khẩu mới phải khác mật khẩu cũ"
            return render_template("change_password.html", err_msg=err_msg)
        if newpassword != confirm:
            err_msg = "Xác nhận mật khẩu không đúng"
            return render_template("change_password.html", err_msg=err_msg)
        try:
            current_user.password = generate_password_hash(newpassword)
            db.session.commit()
            return redirect('/profile')
        except Exception as ex:
            db.session.rollback()
            print(ex)

            err_msg = "Hệ thống đã bị lỗi! Xin vui lòng thử lại sau"
            return render_template("change_password.html", err_msg=err_msg)
    else:
        err_msg = "Mật khẩu cũ không đúng!"
    return render_template("change_password.html", err_msg=err_msg)


@app.route('/lessons')
def lessons():
    lessons = db.session.query(Lesson).filter(Lesson.course_id == 2).all()
    return render_template("lesson.html", lessons=lessons)


@app.route("/lessons/add", methods=["GET", "POST"])
def add_lesson():
    if request.method == "POST":
        video = request.files.get("video")

        video_drive_id = None
        video_url = None

        if video and video.filename:
            filename = secure_filename(video.filename)

            filepath = os.path.join("temp", filename)

            video.save(filepath)

            video_drive_id, video_url = upload_file(
                filepath,
                filename
            )

            os.remove(filepath)

        lesson = LessonContent(
            lesson_id=request.form["lesson_id"],
            title=request.form["title"],
            video_drive_id=video_drive_id,
            video_url=video_url,
            article=request.form.get("article")
        )

        try:
            db.session.add(lesson)
            db.session.commit()

            return redirect("/lesson")

        except Exception as ex:
            db.session.rollback()
            print(ex)
            return "Upload failed"
    return render_template("create_lesson.html")


if __name__ == '__main__':
    app.run(debug=True)
