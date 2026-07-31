from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from __init__ import app, db
from models import (
    User, UserRole, Level,
    Category, Tag, Course, CourseTag,
    Chapter, Lesson,
    Test, Question, Choice,
    UserTest,
    ChatRoom, ChatRoomMessage,
    Enrollment,
    PaymentHistory, PaymentMethod,
    Commission
)


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def seed():
    # ================= USER =================
    users = [
        User(email="admin@ecourse.vn", password=hash_password("123456"),
             name="Nguyễn Văn Admin", role=UserRole.ADMIN),

        User(email="teacher.hoa@ecourse.vn", password=hash_password("123456"),
             name="Trần Thị Hoa", role=UserRole.TEACHER, major="Công nghệ phần mềm"),
        User(email="teacher.nam@ecourse.vn", password=hash_password("123456"),
             name="Lê Văn Nam", role=UserRole.TEACHER, major="Khoa học dữ liệu"),
        User(email="teacher.linh@ecourse.vn", password=hash_password("123456"),
             name="Phạm Thùy Linh", role=UserRole.TEACHER, major="Thiết kế UI/UX"),

        User(email="student.an@ecourse.vn", password=hash_password("123456"),
             name="Đỗ Văn An", role=UserRole.STUDENT, level=Level.JUNIOR),
        User(email="student.binh@ecourse.vn", password=hash_password("123456"),
             name="Vũ Thị Bình", role=UserRole.STUDENT, level=Level.SENIOR),
        User(email="student.cuong@ecourse.vn", password=hash_password("123456"),
             name="Hoàng Văn Cường", role=UserRole.STUDENT, level=Level.MASTER),
        User(email="student.dung@ecourse.vn", password=hash_password("123456"),
             name="Ngô Thị Dung", role=UserRole.STUDENT, level=Level.EXPERT),
    ]
    db.session.add_all(users)
    db.session.commit()

    admin = users[0]
    teachers = users[1:4]
    students = users[4:8]

    # ================= CATEGORY =================
    categories = [
        Category(name="Lập trình Web"),
        Category(name="Khoa học dữ liệu"),
        Category(name="Thiết kế đồ họa"),
        Category(name="Trí tuệ nhân tạo"),
        Category(name="Kỹ năng mềm"),
    ]
    db.session.add_all(categories)
    db.session.commit()

    # ================= TAG =================
    tags = [
        Tag(name="Python"),
        Tag(name="Flask"),
        Tag(name="SQL"),
        Tag(name="Machine Learning"),
        Tag(name="UI/UX"),
        Tag(name="Giao tiếp"),
    ]
    db.session.add_all(tags)
    db.session.commit()

    # ================= COURSE =================
    courses = [
        Course(name="Lập trình Python cơ bản", price=299000,
               category_id=categories[0].id, teacher_id=teachers[0].id,
               description="Khóa học nhập môn Python cho người mới bắt đầu."),
        Course(name="Xây dựng Web với Flask", price=499000,
               category_id=categories[0].id, teacher_id=teachers[0].id,
               description="Học cách xây dựng ứng dụng web bằng Flask và SQLAlchemy."),
        Course(name="Phân tích dữ liệu với Pandas", price=399000,
               category_id=categories[1].id, teacher_id=teachers[1].id,
               description="Xử lý và phân tích dữ liệu với thư viện Pandas."),
        Course(name="Nhập môn Machine Learning", price=599000,
               category_id=categories[3].id, teacher_id=teachers[1].id,
               description="Kiến thức nền tảng về học máy và các thuật toán phổ biến."),
        Course(name="Thiết kế UI/UX cho người mới", price=349000,
               category_id=categories[2].id, teacher_id=teachers[2].id,
               description="Nguyên tắc thiết kế giao diện và trải nghiệm người dùng."),
        Course(name="Figma từ cơ bản đến nâng cao", price=259000,
               category_id=categories[2].id, teacher_id=teachers[2].id,
               description="Thành thạo công cụ thiết kế Figma qua các dự án thực tế."),
        Course(name="Kỹ năng giao tiếp hiệu quả", price=199000,
               category_id=categories[4].id, teacher_id=teachers[0].id,
               description="Rèn luyện kỹ năng giao tiếp và thuyết trình."),
    ]
    db.session.add_all(courses)
    db.session.commit()

    # ================= COURSE_TAG =================
    course_tags = [
        CourseTag(course_id=courses[0].id, tag_id=tags[0].id),   # Python cơ bản - Python
        CourseTag(course_id=courses[1].id, tag_id=tags[0].id),   # Flask - Python
        CourseTag(course_id=courses[1].id, tag_id=tags[1].id),   # Flask - Flask
        CourseTag(course_id=courses[2].id, tag_id=tags[0].id),   # Pandas - Python
        CourseTag(course_id=courses[2].id, tag_id=tags[2].id),   # Pandas - SQL
        CourseTag(course_id=courses[3].id, tag_id=tags[3].id),   # ML - Machine Learning
        CourseTag(course_id=courses[4].id, tag_id=tags[4].id),   # UI/UX - UI/UX
        CourseTag(course_id=courses[6].id, tag_id=tags[5].id),   # Giao tiếp - Giao tiếp
    ]
    db.session.add_all(course_tags)
    db.session.commit()

    # ================= CHAPTER =================
    chapters = [
        Chapter(name="Chương 1: Làm quen với Python", course_id=courses[0].id,
                description="Cài đặt môi trường và cú pháp cơ bản."),
        Chapter(name="Chương 2: Cấu trúc dữ liệu", course_id=courses[0].id,
                description="List, Tuple, Dictionary, Set."),
        Chapter(name="Chương 1: Giới thiệu Flask", course_id=courses[1].id,
                description="Cấu trúc project và routing cơ bản."),
        Chapter(name="Chương 2: Làm việc với SQLAlchemy", course_id=courses[1].id,
                description="Định nghĩa model và truy vấn dữ liệu."),
        Chapter(name="Chương 1: Tổng quan Pandas", course_id=courses[2].id,
                description="DataFrame và Series."),
        Chapter(name="Chương 1: Các thuật toán cơ bản", course_id=courses[3].id,
                description="Hồi quy tuyến tính, phân loại."),
        Chapter(name="Chương 1: Nguyên lý thiết kế", course_id=courses[4].id,
                description="Màu sắc, bố cục, typography."),
        Chapter(name="Chương 1: Kỹ năng thuyết trình", course_id=courses[6].id,
                description="Cách xây dựng và trình bày một bài thuyết trình."),
    ]
    db.session.add_all(chapters)
    db.session.commit()

    # ================= LESSON =================
    lessons = [
        Lesson(chapter_id=chapters[0].id, title="Cài đặt Python và IDE",
               video_url="https://video.ecourse.vn/py-install.mp4"),
        Lesson(chapter_id=chapters[0].id, title="Biến và kiểu dữ liệu",
               video_url="https://video.ecourse.vn/py-variables.mp4"),
        Lesson(chapter_id=chapters[1].id, title="Làm việc với List và Tuple",
               video_url="https://video.ecourse.vn/py-list.mp4"),
        Lesson(chapter_id=chapters[2].id, title="Tạo project Flask đầu tiên",
               video_url="https://video.ecourse.vn/flask-intro.mp4"),
        Lesson(chapter_id=chapters[3].id, title="Định nghĩa model với SQLAlchemy",
               video_url="https://video.ecourse.vn/flask-model.mp4"),
        Lesson(chapter_id=chapters[4].id, title="Đọc dữ liệu từ file CSV",
               video_url="https://video.ecourse.vn/pandas-csv.mp4"),
        Lesson(chapter_id=chapters[5].id, title="Hồi quy tuyến tính là gì?",
               article="Bài viết giới thiệu về hồi quy tuyến tính..."),
        Lesson(chapter_id=chapters[6].id, title="Nguyên lý màu sắc trong thiết kế",
               video_url="https://video.ecourse.vn/uiux-color.mp4"),
        Lesson(chapter_id=chapters[7].id, title="Cấu trúc một bài thuyết trình hay",
               article="Bài viết chia sẻ cấu trúc mở - thân - kết cho bài thuyết trình."),
    ]
    db.session.add_all(lessons)
    db.session.commit()

    # ================= TEST =================
    tests = [
        Test(name="Kiểm tra Chương 1", chapter_id=chapters[0].id,
             description="Kiểm tra kiến thức cơ bản về Python.", total_score=10),
        Test(name="Kiểm tra Chương 2", chapter_id=chapters[1].id,
             description="Kiểm tra kiến thức về cấu trúc dữ liệu.", total_score=10),
        Test(name="Kiểm tra Flask cơ bản", chapter_id=chapters[2].id,
             description="Kiểm tra kiến thức routing trong Flask.", total_score=10),
        Test(name="Kiểm tra SQLAlchemy", chapter_id=chapters[3].id,
             description="Kiểm tra kiến thức về model và quan hệ.", total_score=10),
        Test(name="Kiểm tra Pandas", chapter_id=chapters[4].id,
             description="Kiểm tra kiến thức về DataFrame.", total_score=10),
        Test(name="Kiểm tra thiết kế UI/UX", chapter_id=chapters[6].id,
             description="Kiểm tra kiến thức về nguyên lý thiết kế.", total_score=10),
    ]
    db.session.add_all(tests)
    db.session.commit()

    # ================= QUESTION =================
    questions = [
        Question(test_id=tests[0].id, content="Python là ngôn ngữ lập trình thông dịch hay biên dịch?"),
        Question(test_id=tests[0].id, content="Từ khóa nào dùng để định nghĩa hàm trong Python?"),
        Question(test_id=tests[1].id, content="Kiểu dữ liệu nào trong Python không thể thay đổi (immutable)?"),
        Question(test_id=tests[2].id, content="Decorator nào dùng để định nghĩa route trong Flask?"),
        Question(test_id=tests[3].id, content="Lớp nào trong SQLAlchemy dùng để định nghĩa quan hệ giữa hai bảng?"),
        Question(test_id=tests[4].id, content="Hàm nào dùng để đọc file CSV trong Pandas?"),
    ]
    db.session.add_all(questions)
    db.session.commit()

    # ================= CHOICE =================
    # Chỉ tạo mẫu cho 2 câu hỏi đầu (4 lựa chọn/câu) để đủ khoảng 5-10 bản ghi
    choices = [
        Choice(question_id=questions[0].id, answer="Thông dịch (Interpreted)", is_true=True),
        Choice(question_id=questions[0].id, answer="Biên dịch (Compiled)", is_true=False),
        Choice(question_id=questions[0].id, answer="Cả hai đều đúng", is_true=False),
        Choice(question_id=questions[0].id, answer="Không xác định", is_true=False),

        Choice(question_id=questions[1].id, answer="def", is_true=True),
        Choice(question_id=questions[1].id, answer="function", is_true=False),
        Choice(question_id=questions[1].id, answer="func", is_true=False),
        Choice(question_id=questions[1].id, answer="lambda", is_true=False),
    ]
    db.session.add_all(choices)
    db.session.commit()

    # ================= USER_TEST =================
    user_tests = [
        UserTest(user_id=students[0].id, test_id=tests[0].id, score=8.5),
        UserTest(user_id=students[0].id, test_id=tests[1].id, score=7.0),
        UserTest(user_id=students[1].id, test_id=tests[0].id, score=9.0),
        UserTest(user_id=students[2].id, test_id=tests[2].id, score=6.5),
        UserTest(user_id=students[2].id, test_id=tests[3].id, score=8.0),
        UserTest(user_id=students[3].id, test_id=tests[4].id, score=7.5),
    ]
    db.session.add_all(user_tests)
    db.session.commit()

    # ================= CHAT_ROOM =================
    chat_rooms = [
        ChatRoom(student_id=students[0].id, teacher_id=teachers[0].id, course_id=courses[0].id),
        ChatRoom(student_id=students[1].id, teacher_id=teachers[0].id, course_id=courses[1].id),
        ChatRoom(student_id=students[2].id, teacher_id=teachers[1].id, course_id=courses[2].id),
        ChatRoom(student_id=students[3].id, teacher_id=teachers[1].id, course_id=courses[3].id),
        ChatRoom(student_id=students[0].id, teacher_id=teachers[2].id, course_id=courses[4].id),
    ]
    db.session.add_all(chat_rooms)
    db.session.commit()

    # ================= CHAT_ROOM_MESSAGE =================
    chat_messages = [
        ChatRoomMessage(chat_room_id=chat_rooms[0].id, sender_id=students[0].id,
                         content="Thầy ơi em chưa hiểu về list comprehension ạ."),
        ChatRoomMessage(chat_room_id=chat_rooms[0].id, sender_id=teachers[0].id,
                         content="Em xem lại bài giảng chương 2 nhé, thầy có ví dụ chi tiết."),
        ChatRoomMessage(chat_room_id=chat_rooms[1].id, sender_id=students[1].id,
                         content="Route trong Flask có bắt buộc phải trùng tên hàm không thầy?"),
        ChatRoomMessage(chat_room_id=chat_rooms[1].id, sender_id=teachers[0].id,
                         content="Không bắt buộc, endpoint có thể đặt tên khác em nhé."),
        ChatRoomMessage(chat_room_id=chat_rooms[2].id, sender_id=students[2].id,
                         content="Cô ơi DataFrame và Series khác nhau chỗ nào ạ?"),
        ChatRoomMessage(chat_room_id=chat_rooms[3].id, sender_id=students[3].id,
                         content="Cô cho em hỏi về overfitting trong ML với ạ."),
        ChatRoomMessage(chat_room_id=chat_rooms[3].id, sender_id=teachers[1].id,
                         content="Overfitting là khi mô hình học quá khớp với dữ liệu train, em xem lại slide 12."),
        ChatRoomMessage(chat_room_id=chat_rooms[4].id, sender_id=students[0].id,
                         content="Cô ơi Figma với Adobe XD nên học cái nào trước ạ?"),
    ]
    db.session.add_all(chat_messages)
    db.session.commit()

    # ================= ENROLLMENT =================
    now = datetime.now()
    enrollments = [
        Enrollment(user_id=students[0].id, course_id=courses[0].id,
                   completed_date=now - timedelta(days=2), success_percentage=100),
        Enrollment(user_id=students[0].id, course_id=courses[1].id,
                   success_percentage=45),
        Enrollment(user_id=students[1].id, course_id=courses[0].id,
                   completed_date=now - timedelta(days=10), success_percentage=100),
        Enrollment(user_id=students[2].id, course_id=courses[2].id,
                   success_percentage=60),
        Enrollment(user_id=students[2].id, course_id=courses[3].id,
                   success_percentage=20),
        Enrollment(user_id=students[3].id, course_id=courses[4].id,
                   success_percentage=80),
        Enrollment(user_id=students[3].id, course_id=courses[6].id,
                   completed_date=now - timedelta(days=1), success_percentage=100),
    ]
    db.session.add_all(enrollments)
    db.session.commit()

    # ================= PAYMENT_HISTORY =================
    payments = [
        PaymentHistory(user_id=students[0].id, course_id=courses[0].id,
                        transaction_id="TX0001", payment_method=PaymentMethod.MOMO,
                        price=299000),
        PaymentHistory(user_id=students[0].id, course_id=courses[1].id,
                        transaction_id="TX0002", payment_method=PaymentMethod.VNPAY,
                        price=499000),
        PaymentHistory(user_id=students[1].id, course_id=courses[0].id,
                        transaction_id="TX0003", payment_method=PaymentMethod.MOMO,
                        price=299000),
        PaymentHistory(user_id=students[2].id, course_id=courses[2].id,
                        transaction_id="TX0004", payment_method=PaymentMethod.VNPAY,
                        price=399000),
        PaymentHistory(user_id=students[2].id, course_id=courses[3].id,
                        transaction_id="TX0005", payment_method=PaymentMethod.MOMO,
                        price=599000),
        PaymentHistory(user_id=students[3].id, course_id=courses[4].id,
                        transaction_id="TX0006", payment_method=PaymentMethod.VNPAY,
                        price=349000),
    ]
    db.session.add_all(payments)
    db.session.commit()

    # ================= COMMISSION =================
    commission = Commission()
    db.session.add_all(commission)
    db.session.commit()
    
    
    print("Seed dữ liệu mẫu thành công!")


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed()
