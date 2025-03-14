from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db_postgres import get_user_by_username
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Получаем пользователя из базы данных по имени
        user = get_user_by_username(username)

        # Проверяем пароль
        if user and check_password_hash(user['password_hash'], password):
            # Если пароль правильный, сохраняем пользователя в сессии
            session['login'] = user['id']
            flash('Вы успешно вошли в систему!', 'success')
            # Перенаправляем на защищенную страницу
            return redirect(url_for('home'))
        else:
            flash('Неверные имя пользователя или пароль',
                  'danger')  # Сообщение об ошибке

    return render_template('login.html')


@auth_bp.route('/logout/')
def logout():
    session.clear()
    return redirect('/')
