import enum
from flask_login import UserMixin
from __init__ import app, db


# ================= ENUMS =================
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class Level(enum.Enum):
    JUNIOR = "JUNIOR"
    SENIOR = "SENIOR"
    MASTER = "MASTER"
    EXPERT = "EXPERT"


class PaymentMethod(enum.Enum):
    MOMO = "MOMO"
    VNPAY = "VNPAY"


# ================= BASE MODEL =================
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)


# ================= USER =================
class User(Base, UserMixin):
    __tablename__ = "user"

    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Enum(Level), nullable=True)
    major = db.Column(db.String(80), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)


# ================= Category =================
class Category(Base):
    __tablename__ = "category"
    name = db.Column(db.String(80), nullable=False, unique=True)


# ================= Tag =================
class Tag(Base):
    __tablename__ = "tag"

    name = db.Column(db.String(80), nullable=False, unique=True)


# ================= Course =================
class Course(Base):
    __tablename__ = "course"

    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.ForeignKey('category.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='courses')
    category = db.relationship('Category', backref='courses')


# ================= Course - Tag =================
class CourseTag(Base):
    __tablename__ = "course_tag"

    tag_id = db.Column(db.ForeignKey('tag.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)

    course = db.relationship("Course", backref="course_tags")
    tag = db.relationship("Tag", backref="courses_tags")

    __table_args__ = (db.UniqueConstraint("course_id","tag_id"),)


# ================= Lesson =================
class Lesson(Base):
    __tablename__ = "lesson"

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)

    course = db.relationship("Course", backref=db.backref("lessons", cascade="all, delete-orphan"))



# ================= LessonContent =================
class LessonContent(Base):
    __tablename__ = "lesson_content"

    lesson_id = db.Column(db.ForeignKey("lesson.id", ondelete="CASCADE"), nullable= False)
    title = db.Column(db.String(200), nullable=False)
    video_drive_id = db.Column(db.String(100), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    file_drive_id = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    article = db.Column(db.Text, nullable=True)

    lesson = db.relationship("Lesson", backref=db.backref("lesson_contents", cascade="all, delete-orphan"))

# ================= Test =================
class Test(Base):
    __tablename__ = "test"

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    lesson_id = db.Column(db.ForeignKey('lesson.id', ondelete='CASCADE'), nullable=False)
    total_score = db.Column(db.Float, nullable=True)

    lesson = db.relationship("Lesson", backref=db.backref("tests", cascade="all, delete-orphan"))


# ================= User - Test =================
class UserTest(Base):
    __tablename__ = "user_test"

    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.ForeignKey('test.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)

    user = db.relationship("User", backref="user_tests")
    test = db.relationship("Test", backref="user_tests")

    __table_args__ = (db.UniqueConstraint("user_id","test_id"),)


# ================= Forum =================
class Forum(Base):
    __tablename__ = "forum"

    student_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)

    student = db.relationship("User", foreign_keys=[student_id], backref="student_forums")
    teacher = db.relationship("User", foreign_keys=[teacher_id], backref="teacher_forums")
    course = db.relationship("Course", backref="forums")


# ================= ForumMessage =================
class ForumMessage(Base):
    __tablename__ = "forum_message"

    forum_id = db.Column(db.ForeignKey('forum.id'), nullable=False)
    sender_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id], backref="messages")
    forum = db.relationship("Forum", backref="messages")


# ================= Registered Class =================
class RegisteredClass(Base):
    __tablename__ = "registered_class"

    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    success_percentage = db.Column(db.Float, nullable=True)

    user = db.relationship("User", backref="registered_courses")
    course = db.relationship("Course", backref="registered_courses")

    __table_args__ = (db.UniqueConstraint("user_id","course_id"),)


# ================= Payment History =================
class PaymentHistory(Base):
    __tablename__ = "payment_history"

    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)
    transaction_id = db.Column(db.String(80), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), default=PaymentMethod.MOMO, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref="payments")
    course = db.relationship("Course", backref="payments")

    __table_args__ = (db.UniqueConstraint("user_id", "course_id"),)


# cd vào thư mục ecourseapp rồi chạy python seed_data.py trong Command Prompt để tạo bảng và tạo dữ liệu mẫu

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#
#         db.session.commit()
