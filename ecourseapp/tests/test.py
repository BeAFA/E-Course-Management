import sys
import os
import unittest
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from __init__ import app, db
import models
import dao


class TestECoursePlatform(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()

        # Tạo hậu tố ngẫu nhiên để không bao giờ bị trùng Unique Key
        self.suffix = uuid.uuid4().hex[:6]
        self._seed_initial_data()

    def tearDown(self):
        # Dọn dẹp dữ liệu của ca test vừa chạy để giữ DB sạch
        try:
            # Xóa các liên kết và dữ liệu phụ thuộc
            models.Rating.query.filter_by(course_id=self.course_id).delete()
            models.UserTest.query.filter_by(user_id=self.student_id).delete()
            models.Certificate.query.filter_by(course_id=self.course_id).delete()
            models.Enrollment.query.filter_by(course_id=self.course_id).delete()
            models.PaymentHistory.query.filter_by(course_id=self.course_id).delete()
            models.CourseTag.query.filter_by(course_id=self.course_id).delete()

            # Xóa các bài thi
            models.Test.query.filter(models.Test.id.in_([self.test1_id, self.test2_id])).delete(synchronize_session=False)

            # Xóa chương, khóa học, tag, category và user
            models.Chapter.query.filter_by(id=self.chapter_id).delete()
            models.Course.query.filter_by(id=self.course_id).delete()
            models.Tag.query.filter(models.Tag.name.in_([f"Tag1_{self.suffix}", f"Tag2_{self.suffix}"])).delete(synchronize_session=False)
            models.Category.query.filter_by(name=f"Cat_{self.suffix}").delete()
            models.User.query.filter(models.User.id.in_([self.teacher_id, self.student_id])).delete(synchronize_session=False)

            db.session.commit()
        except Exception:
            db.session.rollback()
        finally:
            self.ctx.pop()

    def _seed_initial_data(self):
        """Tạo dữ liệu mẫu riêng biệt cho từng test"""
        teacher = models.User(
            name=f"GV_{self.suffix}",
            email=f"teacher_{self.suffix}@test.com",
            password=generate_password_hash("123456"),
            role=models.UserRole.TEACHER
        )
        student = models.User(
            name=f"HV_{self.suffix}",
            email=f"student_{self.suffix}@test.com",
            password=generate_password_hash("123456"),
            role=models.UserRole.STUDENT
        )
        db.session.add_all([teacher, student])
        db.session.flush()

        cat = models.Category(name=f"Cat_{self.suffix}")
        tag1 = models.Tag(name=f"Tag1_{self.suffix}")
        tag2 = models.Tag(name=f"Tag2_{self.suffix}")
        db.session.add_all([cat, tag1, tag2])
        db.session.flush()

        course = models.Course(
            name=f"Course_{self.suffix}",
            price=200000,
            category_id=cat.id,
            teacher_id=teacher.id,
            is_active=True
        )
        db.session.add(course)
        db.session.flush()

        chapter = models.Chapter(
            name=f"Chapter_{self.suffix}",
            course_id=course.id,
            is_active=True
        )
        db.session.add(chapter)
        db.session.flush()

        test1 = models.Test(name=f"Test1_{self.suffix}", chapter_id=chapter.id, total_score=10.0, is_active=True)
        test2 = models.Test(name=f"Test2_{self.suffix}", chapter_id=chapter.id, total_score=10.0, is_active=True)
        db.session.add_all([test1, test2])
        db.session.commit()

        self.teacher_id = teacher.id
        self.student_id = student.id
        self.student_email = student.email
        self.course_id = course.id
        self.chapter_id = chapter.id
        self.test1_id = test1.id
        self.test2_id = test2.id

    # ================= 1. KIỂM THỬ XÁC THỰC USER =================

    def test_auth_user_success(self):
        """Kiểm thử đăng nhập thành công với mật khẩu đúng"""
        user = dao.auth_user(self.student_email, "123456")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, self.student_email)

    def test_auth_user_wrong_password(self):
        """Kiểm thử đăng nhập thất bại khi sai mật khẩu"""
        user = dao.auth_user(self.student_email, "sai_mat_khau")
        self.assertIsNone(user)

    # ================= 2. KIỂM THỬ TÍNH TIẾN ĐỘ =================

    def test_course_progress_calculation(self):
        """Kiểm thử tiến độ: hoàn thành 1/2 bài thi = 50%, làm lại không tăng % khống"""
        prog_0 = dao.get_user_course_progress(self.student_id, self.course_id)
        self.assertEqual(prog_0, 0)

        # Nộp bài 1 -> 50%
        ut1 = models.UserTest(user_id=self.student_id, test_id=self.test1_id, score=8.0)
        db.session.add(ut1)
        db.session.commit()
        prog_1 = dao.get_user_course_progress(self.student_id, self.course_id)
        self.assertEqual(prog_1, 50)

        # Nộp lại bài 1 -> vẫn 50% (distinct test)
        ut2 = models.UserTest(user_id=self.student_id, test_id=self.test1_id, score=10.0)
        db.session.add(ut2)
        db.session.commit()
        prog_distinct = dao.get_user_course_progress(self.student_id, self.course_id)
        self.assertEqual(prog_distinct, 50)

        # Nộp bài 2 -> 100%
        ut3 = models.UserTest(user_id=self.student_id, test_id=self.test2_id, score=9.0)
        db.session.add(ut3)
        db.session.commit()
        prog_full = dao.get_user_course_progress(self.student_id, self.course_id)
        self.assertEqual(prog_full, 100)

    # ================= 3. KIỂM THỬ CẤP CHỨNG CHỈ =================

    def test_certificate_issuance_criteria(self):
        """Chỉ cấp chứng chỉ khi tất cả bài thi đạt điểm tối đa"""
        ut1 = models.UserTest(user_id=self.student_id, test_id=self.test1_id, score=8.0)
        ut2 = models.UserTest(user_id=self.student_id, test_id=self.test2_id, score=10.0)
        db.session.add_all([ut1, ut2])
        db.session.commit()

        # Chưa đạt tối đa -> Không cấp
        cert = dao.check_and_issue_certificate(self.student_id, self.course_id)
        self.assertIsNone(cert)

        # Thi lại bài 1 đạt 10/10 -> Cấp chứng chỉ
        ut1_retake = models.UserTest(user_id=self.student_id, test_id=self.test1_id, score=10.0)
        db.session.add(ut1_retake)
        db.session.commit()

        cert = dao.check_and_issue_certificate(self.student_id, self.course_id)
        self.assertIsNotNone(cert)
        self.assertTrue(cert.code.startswith(f"CERT-C{self.course_id}-U{self.student_id}"))

        # Không tạo lặp bản ghi mới
        second_cert = dao.check_and_issue_certificate(self.student_id, self.course_id)
        self.assertEqual(cert.id, second_cert.id)

    # ================= 4. KIỂM THỬ ĐÁNH GIÁ (RATING) =================

    def test_rating_without_enrollment(self):
        """Chưa đăng ký khóa học thì không được đánh giá"""
        rating, err = dao.add_or_update_rating(self.student_id, self.course_id, 5, "Khoa hoc rat tot")
        self.assertIsNone(rating)
        self.assertIn("đăng ký khóa học", err)

    def test_rating_create_and_update_with_enrollment(self):
        """Đã đăng ký thì gửi và cập nhật đánh giá thành công"""
        dao.enroll_course(self.student_id, self.course_id)

        # Đánh giá 4 sao
        rating, err = dao.add_or_update_rating(self.student_id, self.course_id, 4, "Khoa hoc tam on")
        self.assertIsNone(err)
        self.assertEqual(rating.rating, 4)

        stats = dao.get_course_rating_stats(self.course_id)
        self.assertEqual(stats['avg_rating'], 4.0)
        self.assertEqual(stats['rating_count'], 1)

        # Cập nhật thành 5 sao
        rating_upd, err_upd = dao.add_or_update_rating(self.student_id, self.course_id, 5, "Khoa hoc xuat sac")
        self.assertIsNone(err_upd)
        self.assertEqual(rating_upd.rating, 5)

        stats_upd = dao.get_course_rating_stats(self.course_id)
        self.assertEqual(stats_upd['avg_rating'], 5.0)
        self.assertEqual(stats_upd['rating_count'], 1)

    # ================= 5. KIỂM THỬ THỐNG KÊ DOANH THU =================

    def test_teacher_dashboard_revenue_and_stats(self):
        """Kiểm thử tính doanh thu thực nhận (trừ hoa hồng sàn 10%)"""
        dao.save_payment_history(self.student_id, self.course_id, f"TXN_{self.suffix}", 200000)
        dao.enroll_course(self.student_id, self.course_id)

        stats = dao.get_teacher_dashboard_stats(self.teacher_id, commission_rate=0.1)

        self.assertEqual(stats['total_courses'], 1)
        self.assertEqual(stats['total_students'], 1)
        self.assertEqual(stats['net_revenue'], 180000)


if __name__ == '__main__':
    unittest.main()