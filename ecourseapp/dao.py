from werkzeug.security import check_password_hash
from models import User, Course, Chapter, UserRole


def auth_user(email, password):
    user = User.query.filter(User.email == email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_course_by_id(course_id):
    return Course.query.get(course_id)

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