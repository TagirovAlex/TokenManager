import re
from app import db
from app.models import User

MIN_PASSWORD_LENGTH = 8


def _validate_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
    return True


def get_user_by_id(user_id):
    return db.session.get(User, user_id)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def create_user(username, email, password, is_admin=None):
    _validate_password(password)
    
    if User.query.filter_by(username=username).first():
        raise ValueError('Username already exists')
    
    if User.query.filter_by(email=email).first():
        raise ValueError('Email already exists')
    
    # Первый пользователь становится админом
    if User.query.count() == 0:
        is_admin = True
    
    user = User(
        username=username,
        email=email,
        is_admin=is_admin or False
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user_id, **kwargs):
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError('User not found')
    
    if 'username' in kwargs:
        existing = User.query.filter_by(username=kwargs['username']).first()
        if existing and existing.id != user_id:
            raise ValueError('Username already exists')
        user.username = kwargs['username']
    
    if 'email' in kwargs:
        existing = User.query.filter_by(email=kwargs['email']).first()
        if existing and existing.id != user_id:
            raise ValueError('Email already exists')
        user.email = kwargs['email']
    
    if 'password' in kwargs:
        _validate_password(kwargs['password'])
        user.set_password(kwargs['password'])
    
    if 'is_admin' in kwargs:
        user.is_admin = kwargs['is_admin']
    
    if 'is_active' in kwargs:
        user.is_active = kwargs['is_active']
    
    db.session.commit()
    return user


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ValueError('User not found')
    db.session.delete(user)
    db.session.commit()


def authenticate(username, password):
    user = get_user_by_username(username)
    if not user:
        return None
    if not user.is_active:
        return None
    if user.check_password(password):
        return user
    return None


def get_all_users():
    return User.query.all()


def create_admin_user(username, email, password):
    return create_user(username, email, password, is_admin=True)
