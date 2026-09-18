"""
seed_data.py
------------
Script tạo dữ liệu mẫu (5 - 10 bản ghi / model) cho toàn bộ model khai báo
trong models.py của dự án E-Course.

Cách chạy:
    cd vào thư mục chứa __init__.py / models.py rồi chạy:
        python seed_data.py

Lưu ý: script sẽ gọi db.create_all() trước khi seed, nên có thể chạy
trên database rỗng. Nếu database đã có dữ liệu, nên xoá bảng hoặc drop
database trước khi chạy lại để tránh lỗi trùng khoá (unique constraint).
"""

from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from __init__ import app, db
from models import (
    UserRole, Level, PaymentMethod, SenderType,
    User, Category, Tag, Course, Rating, CourseTag, Chapter, Lesson,
    Test, Question, Choice, UserTest, ChatRoom, ChatRoomMessage,
    Enrollment, PaymentHistory,
    AIChatRoom, AIChatRoomMessage, CourseRecommendation,
)


def hash_password(raw_password: str) -> str:
    """Băm mật khẩu bằng werkzeug.security.generate_password_hash."""
    return generate_password_hash(raw_password.strip())


# Ảnh mặc định dùng chung cho dữ liệu mẫu (lấy từ Google Drive).
DEFAULT_AVATAR_DRIVE_ID = "1X-nx8rzQBGGg676PHve-0J-KGYpjJj-1"
DEFAULT_AVATAR_URL = f"https://drive.google.com/uc?id={DEFAULT_AVATAR_DRIVE_ID}"

DEFAULT_COURSE_IMG_DRIVE_ID = "1AvAw7sucIgoV3ytOruFTTEeEt6YOQQY9"
DEFAULT_COURSE_IMG_URL = f"https://drive.google.com/uc?id={DEFAULT_COURSE_IMG_DRIVE_ID}"

DEFAULT_LESSON_IMG_DRIVE_ID = "1DaVBg8l_Ze_b6CB0-4ThfxmIxpxE-ojU"
DEFAULT_LESSON_IMG_URL = f"https://drive.google.com/uc?id={DEFAULT_LESSON_IMG_DRIVE_ID}"


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ================= USER =================
        users = [
            User(email="admin@ecourse.vn", password=hash_password("123456"),
                 name="Nguyễn Văn Admin", role=UserRole.ADMIN,
                 img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="teacher.python@ecourse.vn", password=hash_password("123456"),
                 name="Trần Thị Hồng", major="Công nghệ thông tin", role=UserRole.TEACHER,
                 img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="teacher.web@ecourse.vn", password=hash_password("123456"),
                 name="Lê Minh Tuấn", major="Kỹ thuật phần mềm", role=UserRole.TEACHER,
                 img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="teacher.ai@ecourse.vn", password=hash_password("123456"),
                 name="Phạm Quốc Bảo", major="Khoa học dữ liệu", role=UserRole.TEACHER,
                 img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="student.an@ecourse.vn", password=hash_password("123456"),
                 name="Nguyễn Văn An", level=Level.JUNIOR, major="Công nghệ thông tin",
                 role=UserRole.STUDENT, img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="student.binh@ecourse.vn", password=hash_password("123456"),
                 name="Trần Thị Bình", level=Level.SENIOR, major="Hệ thống thông tin",
                 role=UserRole.STUDENT, img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="student.cuong@ecourse.vn", password=hash_password("123456"),
                 name="Lê Văn Cường", level=Level.MASTER, major="Khoa học máy tính",
                 role=UserRole.STUDENT, img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
            User(email="student.dung@ecourse.vn", password=hash_password("123456"),
                 name="Phạm Thị Dung", level=Level.EXPERT, major="Trí tuệ nhân tạo",
                 role=UserRole.STUDENT, img_drive_id=DEFAULT_AVATAR_DRIVE_ID, img_url=DEFAULT_AVATAR_URL),
        ]
        db.session.add_all(users)
        db.session.commit()

        admin = users[0]
        teachers = [u for u in users if u.role == UserRole.TEACHER]
        students = [u for u in users if u.role == UserRole.STUDENT]

        # ================= CATEGORY =================
        categories = [
            Category(name="Lập trình Web"),
            Category(name="Lập trình di động"),
            Category(name="Khoa học dữ liệu"),
            Category(name="Trí tuệ nhân tạo"),
            Category(name="Cơ sở dữ liệu"),
            Category(name="DevOps & Cloud"),
        ]
        db.session.add_all(categories)
        db.session.commit()

        # ================= TAG =================
        tags = [
            Tag(name="Python"),
            Tag(name="JavaScript"),
            Tag(name="Flask"),
            Tag(name="ReactJS"),
            Tag(name="Machine Learning"),
            Tag(name="SQL"),
        ]
        db.session.add_all(tags)
        db.session.commit()

        # ================= COURSE =================
        courses = [
            Course(name="Lập trình Python cơ bản", price=299000, description="Khoá học Python cho người mới bắt đầu",
                   category_id=categories[0].id, teacher_id=teachers[0].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="Flask - Xây dựng Web App", price=399000, description="Xây dựng ứng dụng web với Flask",
                   category_id=categories[0].id, teacher_id=teachers[0].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="ReactJS từ Zero đến Hero", price=499000, description="Xây dựng giao diện với ReactJS",
                   category_id=categories[0].id, teacher_id=teachers[1].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="Lập trình Android cơ bản", price=349000, description="Xây dựng ứng dụng Android với Java",
                   category_id=categories[1].id, teacher_id=teachers[1].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="Nhập môn Khoa học dữ liệu", price=599000, description="Phân tích dữ liệu với Python",
                   category_id=categories[2].id, teacher_id=teachers[2].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="Machine Learning cơ bản", price=799000, description="Các thuật toán học máy phổ biến",
                   category_id=categories[3].id, teacher_id=teachers[2].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="Thiết kế cơ sở dữ liệu MySQL", price=299000, description="Thiết kế và tối ưu CSDL quan hệ",
                   category_id=categories[4].id, teacher_id=teachers[0].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
            Course(name="Docker & Kubernetes cơ bản", price=459000, description="Triển khai ứng dụng với container",
                   category_id=categories[5].id, teacher_id=teachers[1].id,
                   img_drive_id=DEFAULT_COURSE_IMG_DRIVE_ID, img_url=DEFAULT_COURSE_IMG_URL),
        ]
        db.session.add_all(courses)
        db.session.commit()

        # ================= RATING =================
        ratings = [
            Rating(course_id=courses[0].id, user_id=students[0].id, rating=5,
                   comment="Khoá học rất dễ hiểu, phù hợp cho người mới bắt đầu."),
            Rating(course_id=courses[1].id, user_id=students[0].id, rating=4,
                   comment="Nội dung ổn nhưng phần Flask nâng cao hơi nhanh."),
            Rating(course_id=courses[2].id, user_id=students[1].id, rating=5,
                   comment="Giảng viên dạy React rất cuốn hút."),
            Rating(course_id=courses[3].id, user_id=students[1].id, rating=3,
                   comment="Video hơi khó nghe, mong cải thiện âm thanh."),
            Rating(course_id=courses[4].id, user_id=students[2].id, rating=5,
                   comment="Ví dụ thực tế rất hữu ích cho công việc."),
            Rating(course_id=courses[5].id, user_id=students[2].id, rating=4,
                   comment="Kiến thức Machine Learning được trình bày rõ ràng."),
            Rating(course_id=courses[6].id, user_id=students[3].id, rating=5,
                   comment="Thiết kế CSDL trình bày logic, dễ áp dụng."),
            Rating(course_id=courses[7].id, user_id=students[3].id, rating=2,
                   comment="Phần Kubernetes hơi sơ sài, cần bổ sung thêm."),
        ]
        db.session.add_all(ratings)
        db.session.commit()

        # ================= COURSE - TAG =================
        course_tags = [
            CourseTag(course_id=courses[0].id, tag_id=tags[0].id),
            CourseTag(course_id=courses[1].id, tag_id=tags[0].id),
            CourseTag(course_id=courses[1].id, tag_id=tags[2].id),
            CourseTag(course_id=courses[2].id, tag_id=tags[1].id),
            CourseTag(course_id=courses[2].id, tag_id=tags[3].id),
            CourseTag(course_id=courses[3].id, tag_id=tags[1].id),
            CourseTag(course_id=courses[4].id, tag_id=tags[0].id),
            CourseTag(course_id=courses[5].id, tag_id=tags[4].id),
            CourseTag(course_id=courses[6].id, tag_id=tags[5].id),
            CourseTag(course_id=courses[7].id, tag_id=tags[0].id),
        ]
        db.session.add_all(course_tags)
        db.session.commit()

        # ================= CHAPTER =================
        chapters = [
            Chapter(name="Giới thiệu Python", description="Cài đặt môi trường và cú pháp cơ bản", course_id=courses[0].id),
            Chapter(name="Cấu trúc dữ liệu trong Python", description="List, Tuple, Dict, Set", course_id=courses[0].id),
            Chapter(name="Giới thiệu Flask", description="Cài đặt và routing cơ bản", course_id=courses[1].id),
            Chapter(name="Flask & SQLAlchemy", description="Kết nối và thao tác cơ sở dữ liệu", course_id=courses[1].id),
            Chapter(name="Giới thiệu ReactJS", description="Component, Props, State", course_id=courses[2].id),
            Chapter(name="Giới thiệu Android Studio", description="Tạo dự án Android đầu tiên", course_id=courses[3].id),
            Chapter(name="Thu thập và xử lý dữ liệu", description="Pandas, Numpy cơ bản", course_id=courses[4].id),
            Chapter(name="Hồi quy tuyến tính", description="Linear Regression với Scikit-learn", course_id=courses[5].id),
            Chapter(name="Thiết kế bảng và quan hệ", description="Chuẩn hoá dữ liệu", course_id=courses[6].id),
            Chapter(name="Docker cơ bản", description="Image, Container, Dockerfile", course_id=courses[7].id),
        ]
        db.session.add_all(chapters)
        db.session.commit()

        # ================= LESSON =================
        lessons = [
            Lesson(chapter_id=chapters[0].id, title="Cài đặt Python & IDE", article="Hướng dẫn cài đặt Python và VS Code",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[0].id, title="Biến và kiểu dữ liệu", article="Các kiểu dữ liệu cơ bản trong Python",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[1].id, title="List và Tuple", article="Cách sử dụng List và Tuple",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[2].id, title="Cài đặt Flask", article="Tạo project Flask đầu tiên",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[3].id, title="Kết nối MySQL với Flask", article="Cấu hình SQLAlchemy",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[4].id, title="Tạo Component đầu tiên", article="Function Component trong React",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[5].id, title="Tạo Activity đầu tiên", article="Layout XML cơ bản",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[6].id, title="Đọc dữ liệu với Pandas", article="DataFrame và Series",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[7].id, title="Xây dựng mô hình hồi quy", article="Fit và predict với Scikit-learn",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
            Lesson(chapter_id=chapters[9].id, title="Viết Dockerfile đầu tiên", article="Build image cho ứng dụng Flask",
                   img_drive_id=DEFAULT_LESSON_IMG_DRIVE_ID, img_url=DEFAULT_LESSON_IMG_URL),
        ]
        db.session.add_all(lessons)
        db.session.commit()

        # ================= TEST =================
        tests = [
            Test(name="Kiểm tra Python cơ bản", description="Kiểm tra kiến thức chương 1", chapter_id=chapters[0].id, total_score=10),
            Test(name="Kiểm tra cấu trúc dữ liệu", description="Kiểm tra kiến thức chương 2", chapter_id=chapters[1].id, total_score=10),
            Test(name="Kiểm tra Flask cơ bản", description="Kiểm tra routing và view", chapter_id=chapters[2].id, total_score=10),
            Test(name="Kiểm tra SQLAlchemy", description="Kiểm tra thao tác CSDL", chapter_id=chapters[3].id, total_score=10),
            Test(name="Kiểm tra ReactJS", description="Kiểm tra component & state", chapter_id=chapters[4].id, total_score=10),
            Test(name="Kiểm tra Android cơ bản", description="Kiểm tra Activity & Layout", chapter_id=chapters[5].id, total_score=10),
            Test(name="Kiểm tra Pandas", description="Kiểm tra xử lý dữ liệu", chapter_id=chapters[6].id, total_score=10),
            Test(name="Kiểm tra Machine Learning", description="Kiểm tra hồi quy tuyến tính", chapter_id=chapters[7].id, total_score=10),
        ]
        db.session.add_all(tests)
        db.session.commit()

        # ================= QUESTION & CHOICE =================
        question_bank = [
            (tests[0], "Python là ngôn ngữ lập trình thuộc loại nào?",
             ["Biên dịch", "Thông dịch", "Hợp ngữ", "Máy"], 1),
            (tests[0], "Cách khai báo biến nào sau đây là đúng trong Python?",
             ["int x = 5", "x = 5", "var x = 5", "let x = 5"], 1),
            (tests[1], "Kiểu dữ liệu nào trong Python là không thể thay đổi (immutable)?",
             ["List", "Dict", "Tuple", "Set"], 2),
            (tests[2], "Trong Flask, hàm nào dùng để khai báo route?",
             ["@app.get", "@app.route", "@flask.url", "@app.link"], 1),
            (tests[3], "SQLAlchemy là gì?",
             ["Một framework frontend", "Một ORM cho Python", "Một hệ quản trị CSDL", "Một ngôn ngữ truy vấn"], 1),
            (tests[4], "Trong React, dùng gì để quản lý trạng thái của component?",
             ["Props", "State", "Router", "Context API only"], 1),
            (tests[5], "File layout trong Android Studio có định dạng gì?",
             [".java", ".xml", ".kt", ".gradle"], 1),
            (tests[6], "Thư viện nào dùng để xử lý dữ liệu dạng bảng trong Python?",
             ["Numpy", "Pandas", "Matplotlib", "Requests"], 1),
        ]

        questions = []
        choices = []
        for test, content, options, correct_index in question_bank:
            q = Question(test_id=test.id, content=content)
            questions.append(q)
        db.session.add_all(questions)
        db.session.commit()

        for (test, content, options, correct_index), q in zip(question_bank, questions):
            for idx, option_text in enumerate(options):
                choices.append(
                    Choice(question_id=q.id, answer=option_text, is_true=(idx == correct_index))
                )
        db.session.add_all(choices)
        db.session.commit()

        # ================= USER TEST =================
        user_tests = [
            UserTest(user_id=students[0].id, test_id=tests[0].id, score=8.5),
            UserTest(user_id=students[0].id, test_id=tests[1].id, score=7.0),
            UserTest(user_id=students[1].id, test_id=tests[2].id, score=9.0),
            UserTest(user_id=students[1].id, test_id=tests[3].id, score=6.5),
            UserTest(user_id=students[2].id, test_id=tests[4].id, score=10.0),
            UserTest(user_id=students[2].id, test_id=tests[5].id, score=8.0),
            UserTest(user_id=students[3].id, test_id=tests[6].id, score=7.5),
            UserTest(user_id=students[3].id, test_id=tests[7].id, score=9.5),
        ]
        db.session.add_all(user_tests)
        db.session.commit()

        # ================= CHAT ROOM =================
        chat_rooms = [
            ChatRoom(student_id=students[0].id, teacher_id=teachers[0].id, course_id=courses[0].id),
            ChatRoom(student_id=students[0].id, teacher_id=teachers[0].id, course_id=courses[1].id),
            ChatRoom(student_id=students[1].id, teacher_id=teachers[1].id, course_id=courses[2].id),
            ChatRoom(student_id=students[2].id, teacher_id=teachers[2].id, course_id=courses[4].id),
            ChatRoom(student_id=students[3].id, teacher_id=teachers[2].id, course_id=courses[5].id),
            ChatRoom(student_id=students[1].id, teacher_id=teachers[1].id, course_id=courses[3].id),
        ]
        db.session.add_all(chat_rooms)
        db.session.commit()

        # ================= CHAT ROOM MESSAGE =================
        chat_messages = [
            ChatRoomMessage(chat_room_id=chat_rooms[0].id, sender_id=students[0].id, content="Chào cô, em có thắc mắc về bài List ạ."),
            ChatRoomMessage(chat_room_id=chat_rooms[0].id, sender_id=teachers[0].id, content="Chào em, em cứ hỏi nhé."),
            ChatRoomMessage(chat_room_id=chat_rooms[1].id, sender_id=students[0].id, content="Flask kết nối MySQL như nào ạ cô?"),
            ChatRoomMessage(chat_room_id=chat_rooms[1].id, sender_id=teachers[0].id, content="Em xem lại video bài 5 nhé."),
            ChatRoomMessage(chat_room_id=chat_rooms[2].id, sender_id=students[1].id, content="Thầy ơi useState dùng sao ạ?"),
            ChatRoomMessage(chat_room_id=chat_rooms[2].id, sender_id=teachers[1].id, content="Em xem lại phần state trong bài 5."),
            ChatRoomMessage(chat_room_id=chat_rooms[3].id, sender_id=students[2].id, content="Thầy cho em hỏi về Pandas ạ."),
            ChatRoomMessage(chat_room_id=chat_rooms[4].id, sender_id=students[3].id, content="Mô hình hồi quy tuyến tính khó quá thầy ơi."),
            ChatRoomMessage(chat_room_id=chat_rooms[4].id, sender_id=teachers[2].id, content="Em cứ luyện tập thêm bài tập nhé."),
            ChatRoomMessage(chat_room_id=chat_rooms[5].id, sender_id=students[1].id, content="Android Studio bị lỗi build ạ thầy."),
        ]
        db.session.add_all(chat_messages)
        db.session.commit()

        # ================= ENROLLMENT =================
        enrollments = [
            Enrollment(user_id=students[0].id, course_id=courses[0].id, success_percentage=80,
                       completed_date=None),
            Enrollment(user_id=students[0].id, course_id=courses[1].id, success_percentage=45,
                       completed_date=None),
            Enrollment(user_id=students[1].id, course_id=courses[2].id, success_percentage=100,
                       completed_date=datetime.now() - timedelta(days=5)),
            Enrollment(user_id=students[1].id, course_id=courses[3].id, success_percentage=30,
                       completed_date=None),
            Enrollment(user_id=students[2].id, course_id=courses[4].id, success_percentage=100,
                       completed_date=datetime.now() - timedelta(days=10)),
            Enrollment(user_id=students[2].id, course_id=courses[5].id, success_percentage=60,
                       completed_date=None),
            Enrollment(user_id=students[3].id, course_id=courses[6].id, success_percentage=90,
                       completed_date=None),
            Enrollment(user_id=students[3].id, course_id=courses[7].id, success_percentage=100,
                       completed_date=datetime.now() - timedelta(days=2)),
        ]
        db.session.add_all(enrollments)
        db.session.commit()

        # ================= PAYMENT HISTORY =================
        payments = [
            PaymentHistory(user_id=students[0].id, course_id=courses[0].id, transaction_id="TXN0001",
                            payment_method=PaymentMethod.MOMO, price=courses[0].price),
            PaymentHistory(user_id=students[0].id, course_id=courses[1].id, transaction_id="TXN0002",
                            payment_method=PaymentMethod.VNPAY, price=courses[1].price),
            PaymentHistory(user_id=students[1].id, course_id=courses[2].id, transaction_id="TXN0003",
                            payment_method=PaymentMethod.MOMO, price=courses[2].price),
            PaymentHistory(user_id=students[1].id, course_id=courses[3].id, transaction_id="TXN0004",
                            payment_method=PaymentMethod.VNPAY, price=courses[3].price),
            PaymentHistory(user_id=students[2].id, course_id=courses[4].id, transaction_id="TXN0005",
                            payment_method=PaymentMethod.MOMO, price=courses[4].price),
            PaymentHistory(user_id=students[2].id, course_id=courses[5].id, transaction_id="TXN0006",
                            payment_method=PaymentMethod.VNPAY, price=courses[5].price),
            PaymentHistory(user_id=students[3].id, course_id=courses[6].id, transaction_id="TXN0007",
                            payment_method=PaymentMethod.MOMO, price=courses[6].price),
            PaymentHistory(user_id=students[3].id, course_id=courses[7].id, transaction_id="TXN0008",
                            payment_method=PaymentMethod.VNPAY, price=courses[7].price),
        ]
        db.session.add_all(payments)
        db.session.commit()

        # ================= AI CHAT ROOM =================
        # Mỗi phần tử: (student, tiêu đề đoạn chat)
        ai_chat_rooms = [
            AIChatRoom(user_id=students[0].id, title="Gợi ý khóa học lập trình Python"),
            AIChatRoom(user_id=students[0].id, title="Lộ trình học Machine Learning từ đầu"),
            AIChatRoom(user_id=students[1].id, title="Nên chọn khóa nào cho trình độ Junior?"),
            AIChatRoom(user_id=students[2].id, title="So sánh khóa Thiết kế UI/UX và Frontend"),
        ]
        db.session.add_all(ai_chat_rooms)
        db.session.commit()

        # ================= AI CHAT ROOM MESSAGE =================
        # Mỗi phần tử: (room, người gửi (USER/AI), nội dung, user_id nếu là USER)
        ai_chat_message_data = [
            (ai_chat_rooms[0], SenderType.USER, "Mình chưa biết lập trình, nên bắt đầu từ khóa học nào?", students[0].id),
            (ai_chat_rooms[0], SenderType.AI,
             "Với người mới bắt đầu, mình gợi ý khóa Lập trình Python cơ bản — đi từ cú pháp cơ bản đến làm dự án nhỏ, phù hợp làm nền tảng.", None),
            (ai_chat_rooms[1], SenderType.USER, "Mình biết Python cơ bản rồi, giờ muốn học Machine Learning thì nên học gì tiếp?", students[0].id),
            (ai_chat_rooms[1], SenderType.AI,
             "Bạn có thể học tiếp khóa Machine Learning cơ bản — tập trung vào các thuật toán học máy phổ biến và thực hành.", None),
            (ai_chat_rooms[2], SenderType.USER, "Mình ở trình độ Junior, nên học khóa nào để lên trình độ tiếp theo?", students[1].id),
            (ai_chat_rooms[2], SenderType.AI,
             "Ở trình độ Junior, nên ưu tiên các khóa thực hành nhiều dự án. Bạn muốn theo hướng frontend, backend hay dữ liệu?", None),
            (ai_chat_rooms[3], SenderType.USER, "Khóa ReactJS và khóa thiết kế CSDL khác nhau thế nào? Mình nên học cái nào trước?", students[2].id),
            (ai_chat_rooms[3], SenderType.AI,
             "ReactJS tập trung xây dựng giao diện người dùng, còn thiết kế CSDL tập trung vào việc tổ chức dữ liệu ở backend. Nếu bạn mới bắt đầu, học CSDL trước sẽ giúp hiểu rõ luồng dữ liệu trước khi code giao diện.", None),
        ]

        ai_chat_messages = []
        for room, sender_type, content, user_id in ai_chat_message_data:
            ai_chat_messages.append(
                AIChatRoomMessage(
                    ai_chat_room_id=room.id,
                    user_id=user_id,
                    sender_type=sender_type,
                    content=content,
                )
            )
        db.session.add_all(ai_chat_messages)
        db.session.commit()

        # ================= COURSE RECOMMENDATION =================
        # Gắn khóa học được AI gợi ý vào đúng tin nhắn AI tương ứng ở trên.
        # ai_chat_messages[1] = câu trả lời AI trong ai_chat_rooms[0] -> gợi ý khóa Python cơ bản (courses[0])
        # ai_chat_messages[3] = câu trả lời AI trong ai_chat_rooms[1] -> gợi ý khóa Machine Learning (courses[5])
        # ai_chat_messages[6] = câu trả lời AI trong ai_chat_rooms[3] -> gợi ý khóa Thiết kế CSDL (courses[6])
        course_recommendations = [
            CourseRecommendation(user_id=students[0].id, course_id=courses[0].id,
                                  ai_chat_room_message_id=ai_chat_messages[1].id),
            CourseRecommendation(user_id=students[0].id, course_id=courses[5].id,
                                  ai_chat_room_message_id=ai_chat_messages[3].id),
            CourseRecommendation(user_id=students[2].id, course_id=courses[6].id,
                                  ai_chat_room_message_id=ai_chat_messages[6].id),
        ]
        db.session.add_all(course_recommendations)
        db.session.commit()

        print("Seed dữ liệu mẫu thành công!")
        print(f"- {len(users)} users")
        print(f"- {len(categories)} categories")
        print(f"- {len(tags)} tags")
        print(f"- {len(courses)} courses")
        print(f"- {len(ratings)} ratings")
        print(f"- {len(course_tags)} course_tags")
        print(f"- {len(chapters)} chapters")
        print(f"- {len(lessons)} lessons")
        print(f"- {len(tests)} tests")
        print(f"- {len(questions)} questions / {len(choices)} choices")
        print(f"- {len(user_tests)} user_tests")
        print(f"- {len(chat_rooms)} chat_rooms / {len(chat_messages)} chat_messages")
        print(f"- {len(enrollments)} enrollments")
        print(f"- {len(payments)} payment_history")
        print(f"- {len(ai_chat_rooms)} ai_chat_rooms / {len(ai_chat_messages)} ai_chat_room_messages")
        print(f"- {len(course_recommendations)} course_recommendations")


if __name__ == "__main__":
    seed()