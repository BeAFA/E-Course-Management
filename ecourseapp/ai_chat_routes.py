from google.genai import types
from models import Course, SenderType

MAX_TURNS_SENT = 40

RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "reply": types.Schema(
            type=types.Type.STRING,
            description="Câu trả lời cho học viên, bằng tiếng Việt",
        ),
        "course_ids": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.INTEGER),
            description=(
                "Id của các khóa học (PHẢI nằm trong danh sách được cung cấp) "
                "thực sự phù hợp để gợi ý. Để mảng rỗng nếu không có khóa nào phù hợp."
            ),
        ),
    },
    required=["reply"],
)


def _build_courses_context():
    """Tạo đoạn text mô tả các khóa học đang có, để Gemini biết id nào hợp lệ."""
    courses = Course.query.filter_by(is_active=True).all()
    if not courses:
        return "(Hiện chưa có khóa học nào trong hệ thống.)"
    lines = []
    for c in courses:
        ctx = c.to_ai_context()
        tags = ", ".join(ctx["tags"]) if ctx["tags"] else "không có"
        lines.append(
            f"- id={ctx['id']} | {ctx['name']} | danh mục: {ctx['category']} "
            f"| tag: {tags} | giá: {ctx['price']}đ"
        )
    return "\n".join(lines)


def _serialize_message(msg):
    """Chuyển 1 bản ghi AIChatRoomMessage thành JSON cho frontend,
    kèm khóa học gợi ý còn active (nếu có)."""
    courses = [
        {
            "id": rec.course.id,
            "name": rec.course.name,
            "category": rec.course.category.name if rec.course.category else "",
            "price": rec.course.price or 0,
            "icon": "📘",
        }
        for rec in msg.recommendations
        if rec.is_active
    ]
    return {
        "role": "user" if msg.sender_type == SenderType.USER else "ai",
        "text": msg.content,
        "courses": courses,
    }