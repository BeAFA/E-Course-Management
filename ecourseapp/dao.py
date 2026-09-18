from werkzeug.security import check_password_hash
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from __init__ import db
import models
import random


def auth_user(email, password):
    user = models.User.query.filter(models.User.email == email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None


def get_user_by_id(user_id):
    return models.User.query.get(user_id)


def get_enrolled_courses_by_user(user_id):
    return models.Course.query.join(models.Enrollment, models.Enrollment.course_id == models.Course.id)\
        .filter(models.Enrollment.user_id == user_id, models.Course.is_active == True)\
        .all()


def get_user_course_progress(user_id, course_id):
    """
    Tính tiến độ học tập (%) của học viên trong một khóa học:
    Số bài thi độc nhất đã nộp / Tổng số bài thi active của khóa học.
    """
    active_tests = db.session.query(models.Test.id)\
        .join(models.Chapter, models.Test.chapter_id == models.Chapter.id)\
        .filter(
            models.Chapter.course_id == course_id,
            models.Chapter.is_active == True,
            models.Test.is_active == True
        ).all()
    
    active_test_ids = [t[0] for t in active_tests]
    total_tests = len(active_test_ids)

    if total_tests == 0:
        return 0

    completed_tests_count = db.session.query(db.func.count(db.distinct(models.UserTest.test_id)))\
        .filter(
            models.UserTest.user_id == user_id,
            models.UserTest.test_id.in_(active_test_ids)
        ).scalar() or 0

    progress = round((completed_tests_count / total_tests) * 100)
    return min(progress, 100)


def get_user_completed_test_ids(user_id, course_id):
    """Lấy tập hợp các test_id mà học viên đã hoàn thành trong khóa học này để hiển thị icon tích xanh"""
    records = db.session.query(db.distinct(models.UserTest.test_id))\
        .join(models.Test, models.UserTest.test_id == models.Test.id)\
        .join(models.Chapter, models.Test.chapter_id == models.Chapter.id)\
        .filter(
            models.UserTest.user_id == user_id,
            models.Chapter.course_id == course_id
        ).all()
    return {r[0] for r in records}


def get_courses(kw=None, category_id=None, rating_min=None, price_sort=None):
    query = db.session.query(
        models.Course,
        func.coalesce(func.avg(models.Rating.rating), 0).label('avg_rating'),
        func.count(models.Rating.id).label('rating_count')
    ).outerjoin(
        models.Rating, models.Course.id == models.Rating.course_id
    ).filter(models.Course.is_active == True)

    if kw:
        query = query.outerjoin(models.User, models.Course.teacher_id == models.User.id)
        query = query.filter(or_(
            models.Course.name.icontains(kw),
            models.User.name.icontains(kw)
        ))
        
    if category_id:
        query = query.filter(models.Course.category_id == category_id)

    query = query.group_by(models.Course.id)

    if rating_min:
        query = query.having(func.coalesce(func.avg(models.Rating.rating), 0) >= float(rating_min))

    if price_sort == 'asc':
        query = query.order_by(models.Course.price.asc())
    elif price_sort == 'desc':
        query = query.order_by(models.Course.price.desc())
    else:
        query = query.order_by(models.Course.id.desc())

    results = query.all()
    courses = []
    for course, avg_rating, rating_count in results:
        course.avg_rating = round(float(avg_rating), 1)
        course.rating_count = rating_count
        courses.append(course)
        
    return courses


def get_my_courses(teacher_id):
    return models.Course.query.filter(models.Course.teacher_id == teacher_id).all()


def get_course_by_id(course_id):
    return models.Course.query.get(course_id)


def get_all_tags():
    """Lấy toàn bộ danh sách thẻ tag đang hoạt động để giảng viên lựa chọn"""
    return models.Tag.query.filter_by(is_active=True).all()


def get_course_tag(course_id):
    course_tags = (
        db.session.query(models.CourseTag)
        .filter(models.CourseTag.course_id == course_id)
        .all()
    )
    return [ct.tag.name for ct in course_tags]


def get_categories():
    return models.Category.query.all()


def create_course(name, price, category_id, description, teacher_id, img_drive_id, img_url, tag_ids=None):
    """Tạo và lưu khóa học mới vào cơ sở dữ liệu kèm theo các tag"""
    course = models.Course(
        name=name,
        price=int(price) if price and str(price).isdigit() else 0,
        category_id=int(category_id),
        description=description,
        teacher_id=teacher_id,
        img_drive_id=img_drive_id,
        img_url=img_url,
        is_active=True
    )
    db.session.add(course)
    db.session.flush()

    if tag_ids:
        for tag_id in tag_ids:
            course_tag = models.CourseTag(course_id=course.id, tag_id=int(tag_id))
            db.session.add(course_tag)

    db.session.commit()
    return course


def update_course(course, name, price, category_id, description, img_drive_id, img_url, tag_ids=None):
    course.name = name
    course.price = int(price) if price and str(price).isdigit() else 0
    course.category_id = int(category_id)
    course.description = description
    course.img_drive_id = img_drive_id
    course.img_url = img_url

    if tag_ids is not None:
        models.CourseTag.query.filter_by(course_id=course.id).delete()
        for tag_id in tag_ids:
            course_tag = models.CourseTag(course_id=course.id, tag_id=int(tag_id))
            db.session.add(course_tag)

    db.session.commit()
    return course


# ================= CÁC HÀM XỬ LÝ ĐÁNH GIÁ (RATING) =================

def get_course_rating_stats(course_id):
    """Lấy điểm sao trung bình và số lượng lượt đánh giá của khóa học"""
    result = db.session.query(
        func.coalesce(func.avg(models.Rating.rating), 0).label('avg_rating'),
        func.count(models.Rating.id).label('rating_count')
    ).filter(models.Rating.course_id == course_id).first()

    return {
        'avg_rating': round(float(result.avg_rating), 1),
        'rating_count': result.rating_count
    }


def get_ratings_by_course(course_id, page=1, per_page=10):
    """Phân trang danh sách đánh giá của khóa học"""
    return models.Rating.query.filter(
        models.Rating.course_id == course_id
    ).order_by(
        models.Rating.updated_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)


def get_course_ratings(course_id):
    """Lấy danh sách tất cả các đánh giá của khóa học xếp theo thời gian mới nhất"""
    return models.Rating.query.filter_by(course_id=course_id)\
        .order_by(models.Rating.updated_date.desc()).all()


def get_user_rating_for_course(user_id, course_id):
    """Lấy bản ghi đánh giá của học viên đối với khóa học này (nếu có)"""
    return models.Rating.query.filter_by(user_id=user_id, course_id=course_id).first()


def add_or_update_rating(user_id, course_id, rating_value, comment=None):
    """Tạo mới hoặc chỉnh sửa đánh giá hiện có của học viên"""
    enrolled = models.Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if not enrolled:
        return None, "Bạn cần đăng ký khóa học này trước khi đánh giá."

    rating = models.Rating.query.filter_by(user_id=user_id, course_id=course_id).first()
    if rating:
        rating.rating = int(rating_value)
        rating.comment = comment.strip() if comment else None
    else:
        rating = models.Rating(
            user_id=user_id,
            course_id=course_id,
            rating=int(rating_value),
            comment=comment.strip() if comment else None
        )
        db.session.add(rating)

    try:
        db.session.commit()
        return rating, None
    except Exception as ex:
        db.session.rollback()
        return None, str(ex)


# ================= QUẢN LÝ KHÓA HỌC & CHƯƠNG BÀI =================

def bulk_update_active(course_ids, is_active, teacher_id):
    ids = [int(cid) for cid in course_ids]
    models.Course.query.filter(
        models.Course.id.in_(ids),
        models.Course.teacher_id == teacher_id
    ).update({models.Course.is_active: is_active}, synchronize_session=False)
    db.session.commit()


def get_chapter_by_id(chapter_id):
    return models.Chapter.query.get(chapter_id)


def get_lesson_by_id(lesson_id):
    return models.Lesson.query.get(lesson_id)


def get_test_by_id(test_id):
    return models.Test.query.get(test_id)


def is_course_owner(user, course):
    if not user or not course:
        return False
    return user.role == models.UserRole.TEACHER and course.teacher_id == user.id


def is_chapter_owner(user, chapter):
    if not user or not chapter:
        return False
    return is_course_owner(user, chapter.course)


def update_chapter(chapter, name, description):
    chapter.name = name
    chapter.description = description
    db.session.commit()
    return chapter


def is_lesson_owner(user, lesson):
    if not user or not lesson:
        return False
    return is_chapter_owner(user, lesson.chapter)


# ================= CHAT ROOM =================

def get_or_create_chat_room(student_id, teacher_id, course_id):
    room = models.ChatRoom.query.filter_by(
        student_id=student_id,
        teacher_id=teacher_id,
        course_id=course_id
    ).first()
    
    if not room:
        room = models.ChatRoom(
            student_id=student_id,
            teacher_id=teacher_id,
            course_id=course_id
        )
        db.session.add(room)
        db.session.commit()
        
    return room


def get_chat_room_by_id(room_id):
    return models.ChatRoom.query.get(room_id)


def get_teacher_chat_rooms(course_id, teacher_id):
    return models.ChatRoom.query.filter_by(
        course_id=course_id,
        teacher_id=teacher_id
    ).all()


def get_chat_messages(room_id):
    return models.ChatRoomMessage.query.filter_by(chat_room_id=room_id).order_by(models.ChatRoomMessage.id.asc()).all()


# ================= ĐĂNG KÝ & THANH TOÁN =================

def check_enrollment(user_id, course_id):
    """Kiểm tra học viên đã đăng ký khóa học này chưa"""
    return models.Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()


def enroll_course(user_id, course_id):
    enrollment = models.Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    return enrollment


def save_payment_history(user_id, course_id, transaction_id, price):
    payment = models.PaymentHistory(
        user_id=user_id,
        course_id=course_id,
        transaction_id=transaction_id,
        payment_method=models.PaymentMethod.VNPAY, 
        price=price
    )
    db.session.add(payment)
    db.session.commit()


# ================= THỐNG KÊ TOÀN SÀN CHO ADMIN =================

def get_admin_dashboard_stats(commission_rate=0.1):
    total_sales = db.session.query(
        func.coalesce(func.sum(models.PaymentHistory.price), 0)
    ).scalar() or 0

    total_commission = float(total_sales) * float(commission_rate)

    total_users = models.User.query.filter(models.User.is_active == True).count()
    total_students = models.User.query.filter(
        models.User.role == models.UserRole.STUDENT,
        models.User.is_active == True
    ).count()
    total_teachers = models.User.query.filter(
        models.User.role == models.UserRole.TEACHER,
        models.User.is_active == True
    ).count()

    total_courses = models.Course.query.filter(models.Course.is_active == True).count()
    paid_courses = models.Course.query.filter(
        models.Course.price > 0,
        models.Course.is_active == True
    ).count()
    free_courses = models.Course.query.filter(
        (models.Course.price == 0) | (models.Course.price.is_(None)),
        models.Course.is_active == True
    ).count()

    return {
        'total_commission': total_commission,
        'total_sales': float(total_sales),
        'users': {
            'total': total_users,
            'students': total_students,
            'teachers': total_teachers
        },
        'courses': {
            'total': total_courses,
            'paid': paid_courses,
            'free': free_courses
        }
    }


def get_revenue_chart_data(days=7, commission_rate=0.1):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    results = db.session.query(
        func.date(models.PaymentHistory.created_date).label('date'),
        func.sum(models.PaymentHistory.price).label('revenue')
    ).filter(
        models.PaymentHistory.created_date >= start_date
    ).group_by(
        func.date(models.PaymentHistory.created_date)
    ).order_by(
        func.date(models.PaymentHistory.created_date)
    ).all()

    labels = []
    data = []
    for r in results:
        labels.append(r.date.strftime('%d/%m'))
        revenue_val = float(r.revenue) if r.revenue else 0.0
        commission_value = revenue_val * float(commission_rate)
        data.append(round(commission_value / 1000, 2))

    return {
        'labels': labels,
        'data': data
    }


def get_course_summary_table(kw=None, sort_by='revenue_asc', page=1, per_page=10, commission_rate=0.1):
    base_query = db.session.query(
        models.Course.id.label('course_id'),
        models.Course.name.label('course_name'),
        models.User.name.label('teacher_name'),
        models.Course.price.label('price'),
        func.count(models.Enrollment.id).label('student_count'),
        func.coalesce(func.sum(models.PaymentHistory.price), 0).label('total_revenue')
    ).join(
        models.User, models.Course.teacher_id == models.User.id
    ).outerjoin(
        models.Enrollment, models.Course.id == models.Enrollment.course_id
    ).outerjoin(
        models.PaymentHistory, models.Course.id == models.PaymentHistory.course_id
    )

    if kw:
        base_query = base_query.filter(models.Course.name.ilike(f"%{kw}%"))

    base_query = base_query.group_by(models.Course.id, models.User.id)

    total_records = base_query.count()
    total_pages = (total_records + per_page - 1) // per_page if total_records > 0 else 1

    if sort_by == 'revenue_asc':
        base_query = base_query.order_by(func.coalesce(func.sum(models.PaymentHistory.price), 0).asc())
    elif sort_by == 'revenue_desc':
        base_query = base_query.order_by(func.coalesce(func.sum(models.PaymentHistory.price), 0).desc())
    elif sort_by == 'student_desc':
        base_query = base_query.order_by(func.count(models.Enrollment.id).desc())

    offset = (page - 1) * per_page
    results = base_query.limit(per_page).offset(offset).all()

    items = []
    for item in results:
        revenue_val = float(item.total_revenue) if item.total_revenue else 0.0
        items.append({
            'course_id': f"{item.course_id:03d}",
            'course_name': item.course_name,
            'teacher_name': item.teacher_name,
            'is_paid': 'Có phí' if (item.price and item.price > 0) else 'Miễn phí',
            'student_count': item.student_count,
            'commission': revenue_val * float(commission_rate)
        })

    return {
        'courses': items,
        'total_pages': total_pages,
        'current_page': page
    }


# ================= CHỨNG CHỈ (CERTIFICATE) =================

def check_and_issue_certificate(user_id, course_id):
    """
    Điều kiện cấp chứng chỉ:
    1. Khóa học có ít nhất 1 bài kiểm tra hoạt động.
    2. Tất cả bài thi active (trong các chương active) đều đạt điểm tuyệt đối: max(score) >= test.total_score.
    """
    existing_cert = models.Certificate.query.filter_by(user_id=user_id, course_id=course_id, is_active=True).first()
    if existing_cert:
        return existing_cert

    active_tests = db.session.query(models.Test)\
        .join(models.Chapter, models.Test.chapter_id == models.Chapter.id)\
        .filter(
            models.Chapter.course_id == course_id,
            models.Chapter.is_active == True,
            models.Test.is_active == True
        ).all()

    if not active_tests:
        return None

    for t in active_tests:
        max_score = db.session.query(db.func.max(models.UserTest.score))\
            .filter(
                models.UserTest.user_id == user_id,
                models.UserTest.test_id == t.id
            ).scalar()

        required_score = t.total_score or 10.0
        if max_score is None or max_score < required_score:
            return None

    date_str = datetime.now().strftime('%Y%m%d')
    random_suffix = random.randint(1000, 9999)
    cert_code = f"CERT-C{course_id}-U{user_id}-{date_str}-{random_suffix}"

    new_cert = models.Certificate(
        code=cert_code,
        user_id=user_id,
        course_id=course_id,
        is_active=True
    )
    try:
        db.session.add(new_cert)
        db.session.commit()
        return new_cert
    except Exception as ex:
        db.session.rollback()
        print("Lỗi khi cấp chứng chỉ:", ex)
        return None


def get_user_certificates(user_id):
    """Lấy danh sách chứng chỉ của một học viên"""
    return models.Certificate.query.filter_by(user_id=user_id, is_active=True)\
        .order_by(models.Certificate.created_date.desc()).all()


def get_certificate_by_code(cert_code):
    """Lấy chi tiết một chứng chỉ theo mã"""
    return models.Certificate.query.filter_by(code=cert_code, is_active=True).first()


# ================= DASHBOARD DÀNH CHO GIẢNG VIÊN =================

def get_teacher_dashboard_stats(teacher_id, commission_rate=0.1):
    """
    Thống kê tổng quan cho Giảng viên dựa trên PaymentHistory:
    - Net revenue = Tổng tiền bán khóa học của GV đó * (1 - commission_rate)
    """
    teacher_course_ids = [c.id for c in models.Course.query.filter_by(teacher_id=teacher_id, is_active=True).all()]

    if not teacher_course_ids:
        return {
            'total_courses': 0,
            'total_students': 0,
            'net_revenue': 0,
            'total_certificates': 0
        }

    total_courses = len(teacher_course_ids)

    total_students = db.session.query(func.count(models.Enrollment.id))\
        .filter(models.Enrollment.course_id.in_(teacher_course_ids)).scalar() or 0

    gross_revenue = db.session.query(func.coalesce(func.sum(models.PaymentHistory.price), 0))\
        .filter(models.PaymentHistory.course_id.in_(teacher_course_ids)).scalar() or 0
    
    net_revenue = float(gross_revenue) * (1.0 - float(commission_rate))

    total_certificates = db.session.query(func.count(models.Certificate.id))\
        .filter(
            models.Certificate.course_id.in_(teacher_course_ids),
            models.Certificate.is_active == True
        ).scalar() or 0

    return {
        'total_courses': total_courses,
        'total_students': total_students,
        'net_revenue': round(net_revenue),
        'total_certificates': total_certificates
    }


def get_teacher_course_performance(teacher_id, commission_rate=0.1):
    results = db.session.query(
        models.Course.id,
        models.Course.name,
        models.Course.price,
        models.Category.name.label('category_name'),
        func.count(db.distinct(models.Enrollment.id)).label('student_count'),
        func.coalesce(func.avg(models.Rating.rating), 0).label('avg_rating'),
        func.coalesce(func.sum(models.PaymentHistory.price), 0).label('gross_revenue')
    ).join(models.Category, models.Course.category_id == models.Category.id)\
     .outerjoin(models.Enrollment, models.Course.id == models.Enrollment.course_id)\
     .outerjoin(models.Rating, models.Course.id == models.Rating.course_id)\
     .outerjoin(models.PaymentHistory, models.Course.id == models.PaymentHistory.course_id)\
     .filter(models.Course.teacher_id == teacher_id, models.Course.is_active == True)\
     .group_by(models.Course.id, models.Category.name)\
     .order_by(models.Course.id.desc()).all()

    course_list = []
    for r in results:
        net_rev = float(r.gross_revenue or 0) * (1.0 - float(commission_rate))
        course_list.append({
            'id': r.id,
            'name': r.name,
            'price': r.price or 0,
            'category': r.category_name,
            'students': r.student_count,
            'rating': round(float(r.avg_rating), 1),
            'revenue': round(net_rev)
        })
    return course_list


def get_teacher_revenue_chart(teacher_id, days=7, commission_rate=0.1):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    teacher_course_ids = [c.id for c in models.Course.query.filter_by(teacher_id=teacher_id).all()]
    if not teacher_course_ids:
        return {'labels': [], 'data': []}

    results = db.session.query(
        func.date(models.PaymentHistory.created_date).label('pay_date'),
        func.sum(models.PaymentHistory.price).label('daily_gross')
    ).filter(
        models.PaymentHistory.course_id.in_(teacher_course_ids),
        models.PaymentHistory.created_date >= start_date
    ).group_by(func.date(models.PaymentHistory.created_date))\
     .order_by(func.date(models.PaymentHistory.created_date)).all()

    labels = []
    data = []
    for r in results:
        labels.append(r.pay_date.strftime('%d/%m'))
        net = float(r.daily_gross or 0) * (1.0 - float(commission_rate))
        data.append(round(net))

    return {'labels': labels, 'data': data}