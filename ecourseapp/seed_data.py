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


# =========================================================================
# TÀI NGUYÊN MEDIA CDN TRỰC TIẾP (AVATAR & ẢNH BÌA)
# =========================================================================
AVATARS = {
    "admin": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop",
    "teacher_1": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop",
    "teacher_2": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400&auto=format&fit=crop",
    "teacher_3": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop",
    "student_1": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop",
    "student_2": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop",
    "student_3": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop",
    "student_4": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop"
}

COURSE_COVERS = {
    "python": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop",
    "flask": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&auto=format&fit=crop",
    "react": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=600&auto=format&fit=crop",
    "android": "https://images.unsplash.com/photo-1607252650355-f7fd0460ccdb?w=600&auto=format&fit=crop",
    "datascience": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop",
    "ml": "https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=600&auto=format&fit=crop",
    "mysql": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=600&auto=format&fit=crop",
    "docker": "https://images.unsplash.com/photo-1605745341112-85968b19335b?w=600&auto=format&fit=crop"
}

LESSON_COVERS = {
    "setup": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&auto=format&fit=crop",
    "syntax": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&auto=format&fit=crop",
    "structure": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=600&auto=format&fit=crop",
    "framework": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&auto=format&fit=crop",
    "database": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&auto=format&fit=crop",
    "ui": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=600&auto=format&fit=crop",
    "mobile": "https://images.unsplash.com/photo-1526498460520-4c246339dccb?w=600&auto=format&fit=crop",
    "analysis": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&auto=format&fit=crop",
    "algorithm": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop",
    "cloud": "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?w=600&auto=format&fit=crop"
}


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ================= USER =================
        users = [
            User(email="admin@ecourse.vn", password=hash_password("123456"),
                 name="Nguyễn Văn Admin", role=UserRole.ADMIN,
                 img_drive_id="ecourse/avatars/admin", img_url=AVATARS["admin"]),
            User(email="teacher.python@ecourse.vn", password=hash_password("123456"),
                 name="Trần Thị Hồng", major="Công nghệ thông tin", role=UserRole.TEACHER,
                 img_drive_id="ecourse/avatars/teacher1", img_url=AVATARS["teacher_1"]),
            User(email="teacher.web@ecourse.vn", password=hash_password("123456"),
                 name="Lê Minh Tuấn", major="Kỹ thuật phần mềm", role=UserRole.TEACHER,
                 img_drive_id="ecourse/avatars/teacher2", img_url=AVATARS["teacher_2"]),
            User(email="teacher.ai@ecourse.vn", password=hash_password("123456"),
                 name="Phạm Quốc Bảo", major="Khoa học dữ liệu", role=UserRole.TEACHER,
                 img_drive_id="ecourse/avatars/teacher3", img_url=AVATARS["teacher_3"]),
            User(email="student.an@ecourse.vn", password=hash_password("123456"),
                 name="Nguyễn Văn An", level=Level.JUNIOR, major="Công nghệ thông tin",
                 role=UserRole.STUDENT, img_drive_id="ecourse/avatars/student1", img_url=AVATARS["student_1"]),
            User(email="student.binh@ecourse.vn", password=hash_password("123456"),
                 name="Trần Thị Bình", level=Level.SENIOR, major="Hệ thống thông tin",
                 role=UserRole.STUDENT, img_drive_id="ecourse/avatars/student2", img_url=AVATARS["student_2"]),
            User(email="student.cuong@ecourse.vn", password=hash_password("123456"),
                 name="Lê Văn Cường", level=Level.MASTER, major="Khoa học máy tính",
                 role=UserRole.STUDENT, img_drive_id="ecourse/avatars/student3", img_url=AVATARS["student_3"]),
            User(email="student.dung@ecourse.vn", password=hash_password("123456"),
                 name="Phạm Thị Dung", level=Level.EXPERT, major="Trí tuệ nhân tạo",
                 role=UserRole.STUDENT, img_drive_id="ecourse/avatars/student4", img_url=AVATARS["student_4"]),
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
                   img_drive_id="ecourse/courses/python", img_url=COURSE_COVERS["python"]),
            Course(name="Flask - Xây dựng Web App", price=399000, description="Xây dựng ứng dụng web với Flask",
                   category_id=categories[0].id, teacher_id=teachers[0].id,
                   img_drive_id="ecourse/courses/flask", img_url=COURSE_COVERS["flask"]),
            Course(name="ReactJS từ Zero đến Hero", price=499000, description="Xây dựng giao diện với ReactJS",
                   category_id=categories[0].id, teacher_id=teachers[1].id,
                   img_drive_id="ecourse/courses/react", img_url=COURSE_COVERS["react"]),
            Course(name="Lập trình Android cơ bản", price=349000, description="Xây dựng ứng dụng Android với Java",
                   category_id=categories[1].id, teacher_id=teachers[1].id,
                   img_drive_id="ecourse/courses/android", img_url=COURSE_COVERS["android"]),
            Course(name="Nhập môn Khoa học dữ liệu", price=599000, description="Phân tích dữ liệu với Python",
                   category_id=categories[2].id, teacher_id=teachers[2].id,
                   img_drive_id="ecourse/courses/datascience", img_url=COURSE_COVERS["datascience"]),
            Course(name="Machine Learning cơ bản", price=799000, description="Các thuật toán học máy phổ biến",
                   category_id=categories[3].id, teacher_id=teachers[2].id,
                   img_drive_id="ecourse/courses/ml", img_url=COURSE_COVERS["ml"]),
            Course(name="Thiết kế cơ sở dữ liệu MySQL", price=299000, description="Thiết kế và tối ưu CSDL quan hệ",
                   category_id=categories[4].id, teacher_id=teachers[0].id,
                   img_drive_id="ecourse/courses/mysql", img_url=COURSE_COVERS["mysql"]),
            Course(name="Docker & Kubernetes cơ bản", price=459000, description="Triển khai ứng dụng với container",
                   category_id=categories[5].id, teacher_id=teachers[1].id,
                   img_drive_id="ecourse/courses/docker", img_url=COURSE_COVERS["docker"]),
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

        # ================= LESSON (VIDEO YOUTUBE CHUẨN TỪNG CHUYÊN ĐỀ) =================
        lessons = [
            # 1. Cài đặt Python & VS Code
            Lesson(chapter_id=chapters[0].id, title="Cài đặt Python & IDE", 
                   article="Hướng dẫn tải và cài đặt môi trường Python 3 cùng Visual Studio Code chi tiết cho người mới bắt đầu.",
                   img_drive_id="ecourse/lessons/py_setup", img_url=LESSON_COVERS["setup"],
                   video_drive_id="yt_py_setup", 
                   video_url="https://www.youtube.com/watch?v=YYXdXT2l-Gg"),
            
            # 2. Biến và kiểu dữ liệu Python
            Lesson(chapter_id=chapters[0].id, title="Biến và kiểu dữ liệu", 
                   article="Tìm hiểu các kiểu dữ liệu cơ bản: số nguyên, số thực, chuỗi ký tự và kiểu boolean trong Python.",
                   img_drive_id="ecourse/lessons/py_syntax", img_url=LESSON_COVERS["syntax"],
                   video_drive_id="yt_py_syntax", 
                   video_url="https://www.youtube.com/watch?v=khKv-8q7YmY"),
            
            # 3. List và Tuple trong Python
            Lesson(chapter_id=chapters[1].id, title="List và Tuple", 
                   article="Cấu trúc dữ liệu danh sách (List) và bộ dữ liệu không thay đổi (Tuple) cùng các hàm tiện ích.",
                   img_drive_id="ecourse/lessons/py_struct", img_url=LESSON_COVERS["structure"],
                   video_drive_id="yt_py_struct", 
                   video_url="https://www.youtube.com/watch?v=W8KRzm-HUcc"),
            
            # 4. Bắt đầu với Flask Framework
            Lesson(chapter_id=chapters[2].id, title="Cài đặt Flask", 
                   article="Khởi tạo môi trường ảo venv, cài đặt Flask framework và xây dựng route Hello World đầu tiên.",
                   img_drive_id="ecourse/lessons/flask_init", img_url=LESSON_COVERS["framework"],
                   video_drive_id="yt_flask_init", 
                   video_url="https://www.youtube.com/watch?v=Z1RJmh_Oreq"),
            
            # 5. Kết nối CSDL với Flask & SQLAlchemy
            Lesson(chapter_id=chapters[3].id, title="Kết nối MySQL với Flask", 
                   article="Cấu hình kết nối cơ sở dữ liệu MySQL thông qua Flask-SQLAlchemy và định nghĩa schema model.",
                   img_drive_id="ecourse/lessons/flask_db", img_url=LESSON_COVERS["database"],
                   video_drive_id="yt_flask_db", 
                   video_url="https://www.youtube.com/watch?v=44PvX0Yv368"),
            
            # 6. ReactJS cơ bản - Component & JSX
            Lesson(chapter_id=chapters[4].id, title="Tạo Component đầu tiên", 
                   article="Cấu trúc của React Function Component, cú pháp JSX và cách tổ chức luồng giao diện với Props.",
                   img_drive_id="ecourse/lessons/react_comp", img_url=LESSON_COVERS["ui"],
                   video_drive_id="yt_react_comp", 
                   video_url="https://www.youtube.com/watch?v=bMknfKXIFA8"),
            
            # 7. Android Studio - Tạo Activity & UI XML
            Lesson(chapter_id=chapters[5].id, title="Tạo Activity đầu tiên", 
                   article="Tạo project Android cơ bản, làm quen với giao diện kéo thả XML và chạy ứng dụng trên máy ảo.",
                   img_drive_id="ecourse/lessons/android_act", img_url=LESSON_COVERS["mobile"],
                   video_drive_id="yt_android_act", 
                   video_url="https://www.youtube.com/watch?v=fis26HvvDA4"),
            
            # 8. Phân tích dữ liệu với Pandas
            Lesson(chapter_id=chapters[6].id, title="Đọc dữ liệu với Pandas", 
                   article="Sử dụng Pandas DataFrame để đọc file dữ liệu CSV, lọc dữ liệu và xử lý các giá trị rỗng.",
                   img_drive_id="ecourse/lessons/pandas_read", img_url=LESSON_COVERS["analysis"],
                   video_drive_id="yt_pandas_read", 
                   video_url="https://www.youtube.com/watch?v=vmEHCJofslg"),
            
            # 9. Machine Learning - Mô hình Hồi quy tuyến tính
            Lesson(chapter_id=chapters[7].id, title="Xây dựng mô hình hồi quy", 
                   article="Ứng dụng thuật toán Linear Regression với thư viện Scikit-Learn để dự đoán dữ liệu định lượng.",
                   img_drive_id="ecourse/lessons/ml_reg", img_url=LESSON_COVERS["algorithm"],
                   video_drive_id="yt_ml_reg", 
                   video_url="https://www.youtube.com/watch?v=7eh4d6sabA0"),
            
            # 10. Docker cơ bản cho lập trình viên
            Lesson(chapter_id=chapters[9].id, title="Viết Dockerfile đầu tiên", 
                   article="Khái niệm Image, Container và thực hành viết Dockerfile đóng gói ứng dụng web hoàn chỉnh.",
                   img_drive_id="ecourse/lessons/docker_file", img_url=LESSON_COVERS["cloud"],
                   video_drive_id="yt_docker_file", 
                   video_url="https://www.youtube.com/watch?v=fqMOX6JJhGo"),
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
        for test, content, options, correct_index in question_bank:
            q = Question(test_id=test.id, content=content)
            questions.append(q)
        db.session.add_all(questions)
        db.session.commit()

        choices = []
        for (test, content, options, correct_index), q in zip(question_bank, questions):
            for idx, option_text in enumerate(options):
                choices.append(
                    Choice(question_id=q.id, answer=option_text, is_true=(idx == correct_index))
                )
        db.session.add_all(choices)
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
        ai_chat_rooms = [
            AIChatRoom(user_id=students[0].id, title="Gợi ý khóa học lập trình Python"),
            AIChatRoom(user_id=students[0].id, title="Lộ trình học Machine Learning từ đầu"),
            AIChatRoom(user_id=students[1].id, title="Nên chọn khóa nào cho trình độ Junior?"),
            AIChatRoom(user_id=students[2].id, title="So sánh khóa Thiết kế UI/UX và Frontend"),
        ]
        db.session.add_all(ai_chat_rooms)
        db.session.commit()

        # ================= AI CHAT ROOM MESSAGE =================
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
        print(f"- {len(users)} users (Kèm avatar chuẩn)")
        print(f"- {len(categories)} categories")
        print(f"- {len(tags)} tags")
        print(f"- {len(courses)} courses (Kèm ảnh bìa đúng chủ đề)")
        print(f"- {len(ratings)} ratings")
        print(f"- {len(course_tags)} course_tags")
        print(f"- {len(chapters)} chapters")
        print(f"- {len(lessons)} lessons (Kèm video YouTube chuẩn nội dung bài học)")
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