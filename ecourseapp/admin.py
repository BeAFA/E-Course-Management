from flask import redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from __init__ import app, db
import models
import dao


class DashboardIndexView(AdminIndexView):
    @expose('/')
    def index(self, **kwargs):  # Thêm **kwargs để hứng các keyword arguments từ Flask-Admin
        if not current_user.is_authenticated:
            return redirect(url_for('login_my_user', next=request.url))

        role = getattr(current_user, 'role', None)
        if not (role == models.UserRole.ADMIN or str(role) in ['UserRole.ADMIN', 'ADMIN']):
            return redirect(url_for('login_my_user', next=request.url))

        kw = request.args.get('kw')
        sort_by = request.args.get('sort_by', 'revenue_asc')
        page = request.args.get('page', 1, type=int)
        days = request.args.get('days', 7, type=int)

        COMMISSION_RATE = 0.1

        stats = dao.get_admin_dashboard_stats()
        chart_data = dao.get_revenue_chart_data(days=days, commission_rate=COMMISSION_RATE)
        table_data = dao.get_course_summary_table(
            kw=kw, 
            sort_by=sort_by, 
            page=page, 
            commission_rate=COMMISSION_RATE
        )

        return self.render(
            'admin/dashboard.html',
            stats=stats,
            chart_data=chart_data,
            table_data=table_data,
            kw=kw,
            sort_by=sort_by,
            days=days
        )


class AdminModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        role = getattr(current_user, 'role', None)
        return role == models.UserRole.ADMIN or str(role) in ['UserRole.ADMIN', 'ADMIN']

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login_my_user', next=request.url))


class CourseAdminView(AdminModelView):
    column_list = ['name', 'price', 'category', 'teacher', 'created_date', 'is_active']
    column_searchable_list = ['name', 'description']
    column_filters = ['is_active', 'category', 'teacher', 'created_date']
    column_editable_list = ['is_active']
    column_labels = {
        'name': 'Tên khóa học',
        'price': 'Giá (VNĐ)',
        'category': 'Danh mục',
        'teacher': 'Giảng viên',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class ChapterAdminView(AdminModelView):
    column_list = ['name', 'course', 'created_date', 'is_active']
    column_searchable_list = ['name', 'description']
    column_filters = ['course', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'name': 'Tên chương',
        'course': 'Khóa học',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class LessonAdminView(AdminModelView):
    column_list = ['title', 'chapter', 'created_date', 'is_active']
    column_searchable_list = ['title', 'article']
    column_filters = ['is_active', 'chapter', 'created_date']
    column_editable_list = ['is_active']
    column_labels = {
        'title': 'Tiêu đề bài học',
        'chapter': 'Chương',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class CategoryAdminView(AdminModelView):
    column_list = ['name', 'created_date', 'is_active']
    column_searchable_list = ['name']
    column_filters = ['is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'name': 'Tên danh mục',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class TagAdminView(AdminModelView):
    column_list = ['name', 'created_date', 'is_active']
    column_searchable_list = ['name']
    column_filters = ['is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'name': 'Tên thẻ Tag',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class TestAdminView(AdminModelView):
    column_list = ['name', 'total_score', 'chapter', 'created_date', 'is_active']
    column_searchable_list = ['name', 'description']
    column_filters = ['chapter', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'name': 'Tên bài kiểm tra',
        'total_score': 'Tổng điểm',
        'chapter': 'Chương',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class QuestionAdminView(AdminModelView):
    column_list = ['content', 'test', 'created_date', 'is_active']
    column_searchable_list = ['content']
    column_filters = ['test', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'content': 'Nội dung câu hỏi',
        'test': 'Bài kiểm tra',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class ChoiceAdminView(AdminModelView):
    column_list = ['answer', 'is_true', 'question', 'is_active']
    column_searchable_list = ['answer']
    column_filters = ['is_true', 'question', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'answer': 'Đáp án',
        'is_true': 'Đáp án đúng',
        'question': 'Câu hỏi',
        'is_active': 'Kích hoạt'
    }


class UserTestAdminView(AdminModelView):
    column_list = ['user', 'test', 'score', 'created_date', 'is_active']
    column_searchable_list = ['user.name', 'user.email', 'test.name']
    column_filters = ['test', 'created_date', 'score', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'user': 'Học viên',
        'test': 'Bài kiểm tra',
        'score': 'Điểm số',
        'created_date': 'Thời gian nộp',
        'is_active': 'Trạng thái'
    }


class UserAdminView(AdminModelView):
    column_exclude_list = ['password']
    column_list = ['name', 'email', 'role', 'level', 'major', 'created_date', 'is_active']
    column_searchable_list = ['name', 'email', 'major']
    column_filters = ['role', 'level', 'is_active', 'created_date']
    column_editable_list = ['is_active']
    column_labels = {
        'name': 'Họ và tên',
        'email': 'Địa chỉ Email',
        'role': 'Vai trò',
        'level': 'Trình độ',
        'major': 'Chuyên ngành',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class EnrollmentAdminView(AdminModelView):
    column_list = ['user', 'course', 'success_percentage', 'completed_date', 'created_date', 'is_active']
    column_searchable_list = ['user.name', 'user.email', 'course.name']
    column_filters = ['course', 'created_date', 'completed_date', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'user': 'Học viên',
        'course': 'Khóa học',
        'success_percentage': 'Tiến độ (%)',
        'completed_date': 'Ngày hoàn thành',
        'created_date': 'Ngày đăng ký',
        'is_active': 'Trạng thái'
    }


class PaymentHistoryAdminView(AdminModelView):
    column_list = ['user', 'course', 'price', 'payment_method', 'transaction_id', 'created_date', 'is_active']
    column_searchable_list = ['user.name', 'user.email', 'course.name', 'transaction_id']
    column_filters = ['payment_method', 'course', 'created_date', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'user': 'Người thanh toán',
        'course': 'Khóa học',
        'price': 'Số tiền',
        'payment_method': 'Cổng thanh toán',
        'transaction_id': 'Mã giao dịch',
        'created_date': 'Thời gian',
        'is_active': 'Trạng thái'
    }


class ChatRoomAdminView(AdminModelView):
    column_list = ['student', 'teacher', 'course', 'created_date', 'is_active']
    column_searchable_list = ['student.name', 'teacher.name', 'course.name']
    column_filters = ['course', 'created_date', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'student': 'Học viên',
        'teacher': 'Giảng viên',
        'course': 'Khóa học',
        'created_date': 'Ngày tạo',
        'is_active': 'Kích hoạt'
    }


class ChatRoomMessageAdminView(AdminModelView):
    column_list = ['chat_room', 'sender', 'content', 'created_date', 'is_active']
    column_searchable_list = ['content', 'sender.name', 'sender.email']
    column_filters = ['chat_room', 'created_date', 'is_active']
    column_editable_list = ['is_active']
    column_labels = {
        'chat_room': 'Phòng Chat',
        'sender': 'Người gửi',
        'content': 'Nội dung tin nhắn',
        'created_date': 'Thời gian gửi',
        'is_active': 'Trạng thái'
    }


admin = Admin(app, name='Trang Quản Trị E-Course', index_view=DashboardIndexView(name='Trang chủ'))

admin.add_view(CourseAdminView(models.Course, db.session, name='Khóa học', category='Quản lý Nội dung'))
admin.add_view(ChapterAdminView(models.Chapter, db.session, name='Chương học', category='Quản lý Nội dung'))
admin.add_view(LessonAdminView(models.Lesson, db.session, name='Bài học', category='Quản lý Nội dung'))
admin.add_view(CategoryAdminView(models.Category, db.session, name='Danh mục', category='Quản lý Nội dung'))
admin.add_view(TagAdminView(models.Tag, db.session, name='Thẻ Tag', category='Quản lý Nội dung'))

admin.add_view(TestAdminView(models.Test, db.session, name='Bài kiểm tra', category='Thi & Đánh giá'))
admin.add_view(QuestionAdminView(models.Question, db.session, name='Câu hỏi', category='Thi & Đánh giá'))
admin.add_view(ChoiceAdminView(models.Choice, db.session, name='Đáp án', category='Thi & Đánh giá'))
admin.add_view(UserTestAdminView(models.UserTest, db.session, name='Kết quả thi', category='Thi & Đánh giá'))

admin.add_view(UserAdminView(models.User, db.session, name='Người dùng', category='Tài khoản'))
admin.add_view(EnrollmentAdminView(models.Enrollment, db.session, name='Đăng ký học', category='Tài khoản'))
admin.add_view(PaymentHistoryAdminView(models.PaymentHistory, db.session, name='Lịch sử thanh toán', category='Tài khoản'))

admin.add_view(ChatRoomAdminView(models.ChatRoom, db.session, name='Phòng Chat', category='Tương tác'))
admin.add_view(ChatRoomMessageAdminView(models.ChatRoomMessage, db.session, name='Tin nhắn', category='Tương tác'))