from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

def create_user(erp, name, email, password):
    pw_hash = generate_password_hash(password)
    user = User(erp=erp, name=name, email=email, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    return user

def verify_user(erp, password):
    user = User.query.filter_by(erp=erp).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None
