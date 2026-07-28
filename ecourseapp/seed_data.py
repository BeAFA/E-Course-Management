"""
File tạo dữ liệu mẫu (seed data) cho các model trong models.py
Chạy: python seed_data.py
"""
from werkzeug.security import generate_password_hash
from datetime import datetime

from __init__ import app, db
from models import (
    User, UserRole, Level,
    Category, Tag, Course, CourseTag,
    Lesson, Test, UserTest,
    Forum, ForumMessage,
    RegisteredClass, PaymentHistory, PaymentMethod
)


def hash_pw(raw):
    return generate_password_hash(raw)


def seed():
    with app.app_context():
        # Xoá dữ liệu cũ (nếu có) rồi tạo lại bảng
        db.drop_all()
        db.create_all()

        # ================= USERS =================
        users = [
            User(email="admin@gmail.com", password=hash_pw("123456"),
                 name="Quản trị viên", role=UserRole.ADMIN),
            User(email="teacher1@gmail.com", password=hash_pw("123456"),
                 name="Nguyễn Văn A", role=UserRole.TEACHER, major="Công nghệ thông tin"),
            User(email="teacher2@gmail.com", password=hash_pw("123456"),
                 name="Trần Thị B", role=UserRole.TEACHER, major="Toán học"),
            User(email="teacher3@gmail.com", password=hash_pw("123456"),
                 name="Lê Văn C", role=UserRole.TEACHER, major="Tiếng Anh"),
            User(email="student1@gmail.com", password=hash_pw("123456"),
                 name="Phạm Thị D", role=UserRole.STUDENT, level=Level.JUNIOR, major="CNTT"),
            User(email="student2@gmail.com", password=hash_pw("123456"),
                 name="Hoàng Văn E", role=UserRole.STUDENT, level=Level.SENIOR, major="Kinh tế"),
            User(email="student3@gmail.com", password=hash_pw("123456"),
                 name="Đỗ Thị F", role=UserRole.STUDENT, level=Level.MASTER, major="CNTT"),
            User(email="student4@gmail.com", password=hash_pw("123456"),
                 name="Vũ Văn G", role=UserRole.STUDENT, level=Level.EXPERT, major="Marketing"),
        ]
        db.session.add_all(users)
        db.session.commit()

        admin, teacher1, teacher2, teacher3, student1, student2, student3, student4 = users

        # ================= CATEGORY =================
        categories = [
            Category(name="Lập trình Web"),
            Category(name="Lập trình di động"),
            Category(name="Cơ sở dữ liệu"),
            Category(name="Trí tuệ nhân tạo"),
            Category(name="Ngoại ngữ"),
            Category(name="Kỹ năng mềm"),
        ]
        db.session.add_all(categories)
        db.session.commit()

        cat_web, cat_mobile, cat_db, cat_ai, cat_lang, cat_soft = categories

        # ================= TAG =================
        tags = [
            Tag(name="Python"),
            Tag(name="JavaScript"),
            Tag(name="Flutter"),
            Tag(name="MySQL"),
            Tag(name="Machine Learning"),
            Tag(name="Giao tiếp"),
            Tag(name="Cơ bản"),
        ]
        db.session.add_all(tags)
        db.session.commit()

        tag_python, tag_js, tag_flutter, tag_mysql, tag_ml, tag_comm, tag_basic = tags

        # ================= COURSE =================
        courses = [
            Course(name="Lập trình Python cơ bản", price=500000, category_id=cat_web.id,
                   description="Khoá học nhập môn Python cho người mới bắt đầu.", user_id=teacher1.id),
            Course(name="Xây dựng Web với Flask", price=800000, category_id=cat_web.id,
                   description="Học cách xây dựng ứng dụng web bằng Flask.", user_id=teacher1.id),
            Course(name="Phát triển ứng dụng Flutter", price=900000, category_id=cat_mobile.id,
                   description="Xây dựng app di động đa nền tảng với Flutter.", user_id=teacher2.id),
            Course(name="Thiết kế cơ sở dữ liệu MySQL", price=600000, category_id=cat_db.id,
                   description="Thiết kế và quản trị cơ sở dữ liệu quan hệ.", user_id=teacher2.id),
            Course(name="Nhập môn Machine Learning", price=1200000, category_id=cat_ai.id,
                   description="Kiến thức nền tảng về học máy.", user_id=teacher3.id),
            Course(name="Tiếng Anh giao tiếp cơ bản", price=400000, category_id=cat_lang.id,
                   description="Rèn luyện kỹ năng giao tiếp tiếng Anh.", user_id=teacher3.id),
            Course(name="Kỹ năng thuyết trình", price=300000, category_id=cat_soft.id,
                   description="Nâng cao khả năng thuyết trình trước đám đông.", user_id=teacher1.id),
        ]
        db.session.add_all(courses)
        db.session.commit()

        (course_python, course_flask, course_flutter, course_mysql,
         course_ml, course_english, course_present) = courses

        # ================= COURSE - TAG =================
        course_tags = [
            CourseTag(course_id=course_python.id, tag_id=tag_python.id),
            CourseTag(course_id=course_python.id, tag_id=tag_basic.id),
            CourseTag(course_id=course_flask.id, tag_id=tag_python.id),
            CourseTag(course_id=course_flutter.id, tag_id=tag_flutter.id),
            CourseTag(course_id=course_mysql.id, tag_id=tag_mysql.id),
            CourseTag(course_id=course_ml.id, tag_id=tag_ml.id),
            CourseTag(course_id=course_ml.id, tag_id=tag_python.id),
            CourseTag(course_id=course_english.id, tag_id=tag_comm.id),
            CourseTag(course_id=course_present.id, tag_id=tag_comm.id),
        ]
        db.session.add_all(course_tags)
        db.session.commit()

        # ================= LESSON =================
        lessons = [
            Lesson(name="Giới thiệu Python", description="Cài đặt môi trường và cú pháp cơ bản.",
                   course_id=course_python.id),
            Lesson(name="Biến và kiểu dữ liệu", description="Các kiểu dữ liệu trong Python.",
                   course_id=course_python.id),
            Lesson(name="Giới thiệu Flask", description="Cấu trúc project Flask.",
                   course_id=course_flask.id),
            Lesson(name="Routing trong Flask", description="Định tuyến URL trong Flask.",
                   course_id=course_flask.id),
            Lesson(name="Widget cơ bản trong Flutter", description="Các widget phổ biến.",
                   course_id=course_flutter.id),
            Lesson(name="Thiết kế ERD", description="Cách thiết kế mô hình thực thể liên kết.",
                   course_id=course_mysql.id),
            Lesson(name="Hồi quy tuyến tính", description="Thuật toán Linear Regression.",
                   course_id=course_ml.id),
            Lesson(name="Giao tiếp trong công việc", description="Mẫu câu giao tiếp công sở.",
                   course_id=course_english.id),
        ]
        db.session.add_all(lessons)
        db.session.commit()

        (lesson_py1, lesson_py2, lesson_flask1, lesson_flask2,
         lesson_flutter1, lesson_mysql1, lesson_ml1, lesson_en1) = lessons

        # ================= TEST =================
        tests = [
            Test(name="Kiểm tra Python cơ bản", description="Bài test 15 câu trắc nghiệm.",
                 lesson_id=lesson_py1.id, total_score=10),
            Test(name="Kiểm tra biến & kiểu dữ liệu", description="Bài test thực hành.",
                 lesson_id=lesson_py2.id, total_score=10),
            Test(name="Kiểm tra Routing Flask", description="Bài test về định tuyến.",
                 lesson_id=lesson_flask2.id, total_score=10),
            Test(name="Kiểm tra Widget Flutter", description="Bài test về widget.",
                 lesson_id=lesson_flutter1.id, total_score=10),
            Test(name="Kiểm tra thiết kế ERD", description="Bài test thiết kế CSDL.",
                 lesson_id=lesson_mysql1.id, total_score=10),
            Test(name="Kiểm tra hồi quy tuyến tính", description="Bài test lý thuyết ML.",
                 lesson_id=lesson_ml1.id, total_score=10),
        ]
        db.session.add_all(tests)
        db.session.commit()

        (test_py1, test_py2, test_flask2, test_flutter1,
         test_mysql1, test_ml1) = tests

        # ================= USER - TEST =================
        user_tests = [
            UserTest(user_id=student1.id, test_id=test_py1.id, score=8.5),
            UserTest(user_id=student1.id, test_id=test_py2.id, score=9.0),
            UserTest(user_id=student2.id, test_id=test_flask2.id, score=7.5),
            UserTest(user_id=student3.id, test_id=test_flutter1.id, score=8.0),
            UserTest(user_id=student3.id, test_id=test_mysql1.id, score=9.5),
            UserTest(user_id=student4.id, test_id=test_ml1.id, score=6.5),
        ]
        db.session.add_all(user_tests)
        db.session.commit()

        # ================= FORUM =================
        forums = [
            Forum(student_id=student1.id, teacher_id=teacher1.id, course_id=course_python.id),
            Forum(student_id=student2.id, teacher_id=teacher1.id, course_id=course_flask.id),
            Forum(student_id=student3.id, teacher_id=teacher2.id, course_id=course_flutter.id),
            Forum(student_id=student3.id, teacher_id=teacher2.id, course_id=course_mysql.id),
            Forum(student_id=student4.id, teacher_id=teacher3.id, course_id=course_ml.id),
        ]
        db.session.add_all(forums)
        db.session.commit()

        forum1, forum2, forum3, forum4, forum5 = forums

        # ================= FORUM MESSAGE =================
        forum_messages = [
            ForumMessage(forum_id=forum1.id, sender_id=student1.id,
                         content="Thầy ơi, em không cài được Python ạ."),
            ForumMessage(forum_id=forum1.id, sender_id=teacher1.id,
                         content="Em thử tải lại bản Python 3.11 xem sao."),
            ForumMessage(forum_id=forum2.id, sender_id=student2.id,
                         content="Flask chạy báo lỗi ModuleNotFoundError ạ."),
            ForumMessage(forum_id=forum2.id, sender_id=teacher1.id,
                         content="Em kiểm tra lại đã activate virtualenv chưa nhé."),
            ForumMessage(forum_id=forum3.id, sender_id=student3.id,
                         content="Widget StatefulWidget dùng khi nào ạ thầy?"),
            ForumMessage(forum_id=forum4.id, sender_id=student3.id,
                         content="Em thiết kế ERD này đã chuẩn 3NF chưa ạ?"),
            ForumMessage(forum_id=forum5.id, sender_id=student4.id,
                         content="Cô ơi cho em hỏi công thức hồi quy tuyến tính."),
        ]
        db.session.add_all(forum_messages)
        db.session.commit()

        # ================= REGISTERED CLASS =================
        registered_classes = [
            RegisteredClass(user_id=student1.id, course_id=course_python.id,
                             completed_date=datetime(2026, 6, 1), success_percentage=100),
            RegisteredClass(user_id=student1.id, course_id=course_flask.id,
                             completed_date=None, success_percentage=45),
            RegisteredClass(user_id=student2.id, course_id=course_flask.id,
                             completed_date=datetime(2026, 5, 20), success_percentage=100),
            RegisteredClass(user_id=student3.id, course_id=course_flutter.id,
                             completed_date=datetime(2026, 4, 15), success_percentage=100),
            RegisteredClass(user_id=student3.id, course_id=course_mysql.id,
                             completed_date=None, success_percentage=70),
            RegisteredClass(user_id=student4.id, course_id=course_ml.id,
                             completed_date=None, success_percentage=30),
            RegisteredClass(user_id=student4.id, course_id=course_english.id,
                             completed_date=datetime(2026, 3, 10), success_percentage=100),
        ]
        db.session.add_all(registered_classes)
        db.session.commit()

        # ================= PAYMENT HISTORY =================
        payments = [
            PaymentHistory(user_id=student1.id, course_id=course_python.id,
                            transaction_id="TXN0001", payment_method=PaymentMethod.MOMO,
                            price=500000),
            PaymentHistory(user_id=student1.id, course_id=course_flask.id,
                            transaction_id="TXN0002", payment_method=PaymentMethod.VNPAY,
                            price=800000),
            PaymentHistory(user_id=student2.id, course_id=course_flask.id,
                            transaction_id="TXN0003", payment_method=PaymentMethod.MOMO,
                            price=800000),
            PaymentHistory(user_id=student3.id, course_id=course_flutter.id,
                            transaction_id="TXN0004", payment_method=PaymentMethod.VNPAY,
                            price=900000),
            PaymentHistory(user_id=student3.id, course_id=course_mysql.id,
                            transaction_id="TXN0005", payment_method=PaymentMethod.MOMO,
                            price=600000),
            PaymentHistory(user_id=student4.id, course_id=course_ml.id,
                            transaction_id="TXN0006", payment_method=PaymentMethod.VNPAY,
                            price=1200000),
            PaymentHistory(user_id=student4.id, course_id=course_english.id,
                            transaction_id="TXN0007", payment_method=PaymentMethod.MOMO,
                            price=400000),
        ]
        db.session.add_all(payments)
        db.session.commit()

        print("✅ Đã tạo dữ liệu mẫu thành công!")


if __name__ == "__main__":
    seed()
