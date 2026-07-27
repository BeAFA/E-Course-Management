from werkzeug.security import check_password_hash
from models import User


def auth_user(email, password):
    user = User.query.filter(User.email == email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None

def get_user_by_id(user_id):
    return User.query.get(user_id)