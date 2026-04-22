from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services import auth_service

auth = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        user = auth_service.get_user_by_id(session['user_id'])
        if not user or not user.is_admin:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = auth_service.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            next_url = request.args.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(url_for('web.index'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if password != password_confirm:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            user = auth_service.create_user(username, email, password)
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Регистрация успешна', 'success')
            return redirect(url_for('web.index'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('register.html')


@auth.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = auth_service.get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', user=user)


@auth.route('/change-password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    password_confirm = request.form.get('password_confirm')
    
    user = auth_service.get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))
    
    if not user.check_password(current_password):
        flash('Неверный текущий пароль', 'error')
        return redirect(url_for('auth.profile'))
    
    if new_password != password_confirm:
        flash('Новые пароли не совпадают', 'error')
        return redirect(url_for('auth.profile'))
    
    try:
        auth_service.update_user(session['user_id'], password=new_password)
        flash('Пароль изменен', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('auth.profile'))