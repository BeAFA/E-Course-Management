import unittest
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import app, db
from models import (
    User, Course, Category, Tag, Chapter, Lesson, 
    Enrollment, PaymentHistory, UserRole, PaymentMethod
)
import dao


class ECourseSystemTestCase(unittest.TestCase):
    def setUp(self):
        # Khởi tạo môi trường test với app_context
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        # Mã định danh duy nhất cho mỗi lần test
        self.unique_id = uuid.uuid4().hex[:6]

        # 1. Tạo Category test
        self.category = Category(name=f"Cat_{self.unique_id}")
        db.session.add(self.category)

        # 2. Tạo Tag test
        self.tag_python = Tag(name=f"Py_{self.unique_id}")
        self.tag_flask = Tag(name=f"Fl_{self.unique_id}")
        db.session.add_all([self.tag_python, self.tag_flask])

        # 3. Tạo User test
        self.admin = User(
            email=f"admin_{self.unique_id}@test.com",
            name="Admin Test",
            password=generate_password_hash("123456"),
            role=UserRole.ADMIN,
            img_drive_id="pid_admin",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg"
        )
        self.teacher = User(
            email=f"teacher_{self.unique_id}@test.com",
            name="Teacher Test",
            password=generate_password_hash("123456"),
            role=UserRole.TEACHER,
            img_drive_id="pid_teacher",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg"
        )
        self.student = User(
            email=f"student_{self.unique_id}@test.com",
            name="Student Test",
            password=generate_password_hash("123456"),
            role=UserRole.STUDENT,
            img_drive_id="pid_student",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg"
        )

        db.session.add_all([self.admin, self.teacher, self.student])
        db.session.commit()

    def tearDown(self):
        # Dọn dẹp tài nguyên cơ bản sau mỗi testcase
        try:
            db.session.rollback()
        finally:
            db.session.remove()
            self.app_context.pop()

   
    # Kiểm thử chức năng Đăng ký, Đăng nhập
    def test_user_registration_success(self):
        # Đăng ký tài khoản học viên mới và mã hóa mật khẩu
        email = f"new_stu_{self.unique_id}@test.com"
        new_user = User(
            name="New Student",
            email=email,
            password=generate_password_hash("password123"),
            role=UserRole.STUDENT,
            img_drive_id="pid_default",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg"
        )
        db.session.add(new_user)
        db.session.commit()

        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.email, email)

    def test_user_login_authentication(self):
        #Xác thực đăng nhập đúng và sai mật khẩu
        user = User.query.filter_by(email=self.student.email).first()
        self.assertIsNotNone(user)

        # Mật khẩu đúng
        self.assertTrue(check_password_hash(user.password, "123456"))

        # Mật khẩu sai
        self.assertFalse(check_password_hash(user.password, "wrongpassword"))

    # Kiểm thử chức năng Lọc và Tìm kiếm khóa học
    def test_course_search_and_filter(self):
        # Tìm kiếm khóa học theo từ khóa và danh mục
        kw_test = f"SpecialKW_{self.unique_id}"
        c1 = dao.create_course(
            name=f"Khoa hoc {kw_test}",
            price=200000,
            category_id=self.category.id,
            description="Lập trình web bằng Flask",
            teacher_id=self.teacher.id,
            img_drive_id="pid_c1",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            tag_ids=[self.tag_python.id]
        )

        results_kw = dao.get_courses(kw=kw_test)
        self.assertTrue(any(c.id == c1.id for c in results_kw))

        results_cat = dao.get_courses(category_id=self.category.id)
        self.assertTrue(any(c.id == c1.id for c in results_cat))

   
    # Đăng ký và Thanh toán khóa học
    def test_course_enrollment_and_payment(self):
        # Đăng ký khóa học và lưu lịch sử giao dịch
        course = dao.create_course(
            name=f"Payment Course {self.unique_id}",
            price=300000,
            category_id=self.category.id,
            description="Python chuyên sâu",
            teacher_id=self.teacher.id,
            img_drive_id="pid_pay",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            tag_ids=[]
        )

        enrollment = dao.enroll_course(user_id=self.student.id, course_id=course.id)
        self.assertIsNotNone(enrollment)
        self.assertEqual(enrollment.user_id, self.student.id)

        txn_id = f"TXN_{self.unique_id}"
        payment = PaymentHistory(
            user_id=self.student.id,
            course_id=course.id,
            transaction_id=txn_id,
            payment_method=PaymentMethod.VNPAY,
            price=course.price
        )
        db.session.add(payment)
        db.session.commit()

        saved_payment = PaymentHistory.query.filter_by(transaction_id=txn_id).first()
        self.assertIsNotNone(saved_payment)
        self.assertEqual(saved_payment.price, 300000)

    # Thêm, Sửa khóa học
    def test_course_crud_operations(self):
        # Tạo mới và cập nhật thông tin khóa học
        # 1. Thêm mới khóa học
        course = dao.create_course(
            name=f"CRUD Course {self.unique_id}",
            price=100000,
            category_id=self.category.id,
            description="Mô tả ban đầu",
            teacher_id=self.teacher.id,
            img_drive_id="pid_crud",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            tag_ids=[self.tag_python.id]
        )
        course_id = course.id
        self.assertIsNotNone(course_id)

        # 2. Chỉnh sửa thông tin khóa học
        dao.update_course(
            course=course,
            name=f"Updated Course {self.unique_id}",
            price=150000,
            category_id=self.category.id,
            description="Mô tả cập nhật",
            img_drive_id="pid_test_update",
            img_url="https://res.cloudinary.com/demo/image/upload/sample2.jpg",
            tag_ids=[self.tag_flask.id]
        )
        updated = dao.get_course_by_id(course_id)
        self.assertEqual(updated.name, f"Updated Course {self.unique_id}")
        self.assertEqual(updated.price, 150000)

    # Thêm, Sửa nội dung khóa học
    def test_course_content_crud(self):
        # Tạo chương học và thêm/sửa bài học trong chương
        # 1. Tạo khóa học
        course = dao.create_course(
            name=f"Content Course {self.unique_id}",
            price=0,
            category_id=self.category.id,
            description="Khóa học kiểm tra nội dung",
            teacher_id=self.teacher.id,
            img_drive_id="pid_content",
            img_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
            tag_ids=[]
        )

        # 2. Thêm chương học
        chapter = Chapter(name="Chương 1: Khởi đầu", description="Nội dung khởi đầu", course_id=course.id)
        db.session.add(chapter)
        db.session.commit()
        self.assertIsNotNone(chapter.id)

        # 3. Thêm bài học mới
        lesson = Lesson(
            chapter_id=chapter.id,
            title="Bài 1: Cài đặt công cụ",
            article="Nội dung hướng dẫn chi tiết",
            video_url="https://res.cloudinary.com/demo/video/upload/sample.mp4"
        )
        db.session.add(lesson)
        db.session.commit()
        self.assertIsNotNone(lesson.id)

        # 4. Chỉnh sửa bài học
        lesson.title = "Bài 1: Cài đặt công cụ (Bản mới)"
        db.session.commit()
        self.assertEqual(db.session.get(Lesson, lesson.id).title, "Bài 1: Cài đặt công cụ (Bản mới)")


    # Quản lý trang cá nhân
    def test_user_profile_management(self):
        # Cập nhật thông tin cá nhân và mật khẩu
        user = self.student
        user.name = "Ten Moi Test"
        user.major = "Khoa hoc may tinh"
        db.session.commit()

        updated_user = db.session.get(User, user.id)
        self.assertEqual(updated_user.name, "Ten Moi Test")

        new_password = "newpassword456"
        user.password = generate_password_hash(new_password)
        db.session.commit()

        user_check = db.session.get(User, user.id)
        self.assertTrue(check_password_hash(user_check.password, new_password))


if __name__ == '__main__':
    unittest.main()