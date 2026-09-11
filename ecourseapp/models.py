import enum
from flask_login import UserMixin
from sqlalchemy import func
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


class SenderType(enum.Enum):
    USER = "USER"
    AI = "AI"


class PaymentMethod(enum.Enum):
    MOMO = "MOMO"
    VNPAY = "VNPAY"


# ================= BASE MODEL =================
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=db.func.now())
    updated_date = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    is_active = db.Column(db.Boolean, default=True)


# ================= USER =================
class User(Base, UserMixin):
    __tablename__ = "user"

    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    img_drive_id = db.Column(db.String(100), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Enum(Level), nullable=True)
    major = db.Column(db.String(80), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)

    courses = db.relationship("Course", back_populates="teacher")
    user_tests = db.relationship("UserTest", back_populates="user")
    student_chats = db.relationship(
        "ChatRoom", foreign_keys="ChatRoom.student_id", back_populates="student"
    )
    teacher_chats = db.relationship(
        "ChatRoom", foreign_keys="ChatRoom.teacher_id", back_populates="teacher"
    )
    messages = db.relationship(
        "ChatRoomMessage", foreign_keys="ChatRoomMessage.sender_id", back_populates="sender"
    )
    ai_chat_room_messages = db.relationship("AIChatRoomMessage", foreign_keys="AIChatRoomMessage.user_id",
                                            back_populates="user")
    user_chats = db.relationship("AIChatRoom", foreign_keys="AIChatRoom.user_id", back_populates="user")
    course_recommendations = db.relationship("CourseRecommendation", back_populates="user")
    enrollments = db.relationship("Enrollment", back_populates="user")
    payments = db.relationship("PaymentHistory", back_populates="user")
    ratings = db.relationship("Rating", back_populates="user")

    def __str__(self):
        return self.name


# ================= Category =================
class Category(Base):
    __tablename__ = "category"
    name = db.Column(db.String(80), nullable=False, unique=True)

    courses = db.relationship("Course", back_populates="category")

    def __str__(self):
        return self.name


# ================= Tag =================
class Tag(Base):
    __tablename__ = "tag"

    name = db.Column(db.String(80), nullable=False, unique=True)

    courses_tags = db.relationship("CourseTag", back_populates="tag")

    def __str__(self):
        return self.name


# ================= Course =================
class Course(Base):
    __tablename__ = "course"

    img_drive_id = db.Column(db.String(100), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.ForeignKey('category.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.ForeignKey('user.id'), nullable=False)

    teacher = db.relationship('User', back_populates='courses')
    category = db.relationship('Category', back_populates='courses')

    course_tags = db.relationship("CourseTag", back_populates="course")
    chapters = db.relationship(
        "Chapter",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    chats = db.relationship("ChatRoom", back_populates="course")
    recommendations = db.relationship("CourseRecommendation", back_populates="course")
    enrollments = db.relationship("Enrollment", back_populates="course")
    payments = db.relationship("PaymentHistory", back_populates="course")
    ratings = db.relationship("Rating", back_populates="course")

    def __str__(self):
        return self.name

    def to_ai_context(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
            "tags": [ct.tag.name for ct in self.course_tags],
            "price": self.price,
            "desc": (self.description or "")[:100]
        }


# ================= Rating =================
class Rating(Base):
    __tablename__ = "rating"

    course_id = db.Column(db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False, default=5)
    comment = db.Column(db.Text, nullable=True)

    course = db.relationship("Course", back_populates="ratings")
    user = db.relationship("User", back_populates="ratings")

    __table_args__ = (
        db.UniqueConstraint(
            "course_id",
            "user_id",
            name="uq_course_user_rating"
        ),
    )


# ================= Course - Tag =================
# Nếu bảng trung gian không cần thêm field nào và chỉ dùng để nối, SQLAlchemy cho phép dùng secondary=
# (association table đơn giản, không cần model riêng) — gọn hơn là tạo hẳn 1 class như CourseTag.
class CourseTag(Base):
    __tablename__ = "course_tag"

    tag_id = db.Column(db.ForeignKey('tag.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)

    course = db.relationship("Course", back_populates="course_tags")
    tag = db.relationship("Tag", back_populates="courses_tags")

    __table_args__ = (db.UniqueConstraint("course_id", "tag_id"),)


# ================= Chapter =================
class Chapter(Base):
    __tablename__ = "chapter"

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    course_id = db.Column(db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)

    course = db.relationship("Course", back_populates="chapters")

    lessons = db.relationship(
        "Lesson",
        back_populates="chapter",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    test = db.relationship(
        "Test",
        back_populates="chapter",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self):
        return self.name


# ================= Lesson =================
class Lesson(Base):
    __tablename__ = "lesson"

    chapter_id = db.Column(db.ForeignKey("chapter.id", ondelete="CASCADE"), nullable=False)
    img_drive_id = db.Column(db.String(100), nullable=True)
    img_url = db.Column(db.String(500), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    video_drive_id = db.Column(db.String(100), nullable=True)
    video_url = db.Column(db.String(500), nullable=True)
    file_drive_id = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    article = db.Column(db.Text, nullable=True)

    chapter = db.relationship("Chapter", back_populates="lessons")

    def __str__(self):
        return self.name


# ================= Test =================
class Test(Base):
    __tablename__ = "test"

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    chapter_id = db.Column(db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_score = db.Column(db.Float, nullable=True)

    chapter = db.relationship("Chapter", back_populates="test")

    questions = db.relationship(
        "Question",
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    user_tests = db.relationship("UserTest", back_populates="test")

    def __str__(self):
        return self.name


# ================= Question =================
class Question(Base):
    __tablename__ = "question"

    test_id = db.Column(db.ForeignKey('test.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    test = db.relationship("Test", back_populates="questions")

    choices = db.relationship(
        "Choice",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __str__(self):
        return self.content[0:15] + "..."


# ================= Choice =================
class Choice(Base):
    __tablename__ = "choice"

    question_id = db.Column(db.ForeignKey('question.id', ondelete="CASCADE"), nullable=False)
    answer = db.Column(db.String(80), nullable=False)
    is_true = db.Column(db.Boolean, default=False, nullable=False)

    question = db.relationship("Question", back_populates="choices")

    def __str__(self):
        return self.answer[:15] + "..."


# ================= User - Test =================
class UserTest(Base):
    __tablename__ = "user_test"

    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    test_id = db.Column(db.ForeignKey('test.id'), nullable=False)
    score = db.Column(db.Float, nullable=True)

    user = db.relationship("User", back_populates="user_tests")
    test = db.relationship("Test", back_populates="user_tests")


# ================= ChatRoom =================
class ChatRoom(Base):
    __tablename__ = "chat_room"

    student_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    teacher_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)

    student = db.relationship("User", foreign_keys=[student_id], back_populates="student_chats")
    teacher = db.relationship("User", foreign_keys=[teacher_id], back_populates="teacher_chats")
    course = db.relationship("Course", back_populates="chats")

    messages = db.relationship("ChatRoomMessage", back_populates="chat_room")

    __table_args__ = (db.UniqueConstraint("student_id", "teacher_id", "course_id"),)

    def __str__(self):
        return self.student.name + "_" + self.teacher.name


# ================= ChatRoomMessage =================
class ChatRoomMessage(Base):
    __tablename__ = "chat_room_message"

    chat_room_id = db.Column(db.ForeignKey('chat_room.id'), nullable=False)
    sender_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id], back_populates="messages")
    chat_room = db.relationship("ChatRoom", back_populates="messages")


# ================= AI Chat Room=================
class AIChatRoom(Base):
    __tablename__ = "ai_chat_room"

    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)

    ai_chat_messages = db.relationship("AIChatRoomMessage", back_populates="ai_chat_room", cascade="all, delete-orphan",
                                       passive_deletes=True, )
    user = db.relationship("User", back_populates="user_chats")

    def __str__(self):
        return self.user.name


# ================= AI Message =================
class AIChatRoomMessage(Base):
    __tablename__ = "ai_chat_room_message"

    ai_chat_room_id = db.Column(db.ForeignKey('ai_chat_room.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True)
    sender_type = db.Column(db.Enum(SenderType), nullable=False, default=SenderType.USER)
    content = db.Column(db.Text, nullable=False)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="ai_chat_room_messages")
    ai_chat_room = db.relationship("AIChatRoom", back_populates="ai_chat_messages")
    recommendations = db.relationship(
        "CourseRecommendation",
        back_populates="ai_chat_room_message",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ================= Course Recommendation =================
class CourseRecommendation(Base):
    __tablename__ = "course_recommendation"

    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id', ondelete='CASCADE'), nullable=False)
    ai_chat_room_message_id = db.Column(
        db.ForeignKey('ai_chat_room_message.id', ondelete='CASCADE'), nullable=False
    )

    user = db.relationship("User", back_populates="course_recommendations")
    course = db.relationship("Course", back_populates="recommendations")
    ai_chat_room_message = db.relationship("AIChatRoomMessage", back_populates="recommendations")

    __table_args__ = (db.UniqueConstraint("ai_chat_room_message_id", "course_id"),)


# ================= Registered Class =================
class Enrollment(Base):
    __tablename__ = "enrollment"

    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)
    completed_date = db.Column(db.DateTime, nullable=True)
    success_percentage = db.Column(db.Float, nullable=True)

    user = db.relationship("User", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")

    __table_args__ = (db.UniqueConstraint("user_id", "course_id"),)


# ================= Payment History =================
class PaymentHistory(Base):
    __tablename__ = "payment_history"

    user_id = db.Column(db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.ForeignKey('course.id'), nullable=False)
    transaction_id = db.Column(db.String(80), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethod), default=PaymentMethod.MOMO, nullable=False)
    price = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", back_populates="payments")
    course = db.relationship("Course", back_populates="payments")


# ================= Commission =================
class Commission(Base):
    __tablename__ = "commission"

    total_amount = db.Column(db.Float, default=0.0, nullable=False)

    @classmethod
    def add_commission(cls, amount):
        commission = cls.query.first()
        if not commission:
            commission = cls(total_amount=amount)
            db.session.add(commission)
        else:
            commission.total_amount += amount
        db.session.commit()
        return commission.total_amount

# cd vào thư mục ecourseapp rồi chạy python seed_data.py trong Command Prompt để tạo bảng và tạo dữ liệu mẫu

# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#
#         db.session.commit()
