from werkzeug.security import check_password_hash
from models import User, Course, Category, Chapter, UserRole, Lesson
from sqlalchemy import func
from datetime import datetime, timedelta
from __init__ import db


def auth_user(email, password):
    user = User.query.filter(User.email == email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_user_by_id(user_id):
    return User.query.get(user_id)

def get_courses(kw=None, category_id=None):
    query = Course.query.filter_by(is_active=True)

    if kw:
        query = query.filter(Course.name.icontains(kw))

    if category_id:
        query = query.filter(Course.category_id == category_id)

    return query.all()


def get_course_by_id(course_id):
    return Course.query.get(course_id)

def get_categories():
    return Category.query.all()

def create_course(name, price, category_id, description, user_id):
    """Tạo và lưu khóa học mới vào cơ sở dữ liệu"""
    course = Course(
        name=name,
        price=int(price) if price and price.isdigit() else 0,
        category_id=int(category_id),
        description=description,
        user_id=user_id
    )
    db.session.add(course)
    db.session.commit()
    return course

def get_chapter_by_id(chapter_id):
    return Chapter.query.get(chapter_id)

def get_lesson_by_id(lesson_id):
    return Lesson.query.get(lesson_id)

def is_course_owner(user, course):
    if not user or not course:
        return False
    return user.role == UserRole.TEACHER and course.teacher_id == user.id

def is_chapter_owner(user, chapter):
    if not user or not chapter:
        return False
    return is_course_owner(user, chapter.course)

def is_lesson_owner(user, lesson):
    if not user or not lesson:
        return False
    return is_chapter_owner(user, lesson.chapter)
  
def get_admin_dashboard_stats():
    commission_record = models.Commission.query.first()
    total_commission = commission_record.total_amount if commission_record else 0.0

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
