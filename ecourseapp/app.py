from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, redirect
from __init__ import app, db, login
from models import User, UserRole, Level, Course
import dao


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
    #Xóa các comment ở dưới nếu muốn kiểm tra đăng nhập và quyền
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
@app.route('/profile/updateprofile', methods=["GET", "POST"])
def profile():
    levels = list(Level)
    if not current_user.is_authenticated:
        return redirect("/login")

    if request.method == "POST":
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
            return render_template("profile.html", user=current_user, levels=levels, err_msg=err_msg)

    return render_template("profile.html", user=current_user, levels=levels)


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


if __name__ == '__main__':
    app.run(debug=True)
