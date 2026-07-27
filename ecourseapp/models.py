import enum
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from __init__ import app, db


# ================= ENUMS =================
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class Level(enum.Enum):
    JUNIOR = "JUNIOR"
    SENIOR = "SENIOR"
    MASTER = "MASTER"
    EXPERT = "EXPERT"


# ================= BASE MODEL =================
class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_date = db.Column(db.DateTime, default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)


# ================= USER & ACCOUNT SYSTEM =================
class User(Base, UserMixin):
    __tablename__ = "user"

    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    level = db.Column(db.Enum(Level), nullable=True)
    major = db.Column(db.String(80), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        db.session.commit()