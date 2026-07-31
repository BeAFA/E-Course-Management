from werkzeug.security import check_password_hash
from models import User, Course, Category, Chapter, UserRole
from __init__ import db


def auth_user(email, password):
    user = User.query.filter(User.email == email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_courses(kw=None, category_id=None):
    query = Course.query.filter_by(is_active=True)

    if kw:
        query = query.filter(Course.name.icontains(kw))

    if category_id:
        query = query.filter(Course.category_id == category_id)

    return query.all()


def get_course_by_id(course_id):
    return Course.query.get(course_id)

def get_categories():
    return Category.query.all()

def create_course(name, price, category_id, description, user_id):
    """Tạo và lưu khóa học mới vào cơ sở dữ liệu"""
    course = Course(
        name=name,
        price=int(price) if price and price.isdigit() else 0,
        category_id=int(category_id),
        description=description,
        user_id=user_id
    )
    db.session.add(course)
    db.session.commit()
    return course

def get_chapter_by_id(chapter_id):
    return Chapter.query.get(chapter_id)

def is_course_owner(user, course):
    if not user or not course:
        return False
    return user.role == UserRole.TEACHER and course.teacher_id == user.id

def is_chapter_owner(user, chapter):
    if not user or not chapter:
        return False
    return is_course_owner(user, chapter.course)
