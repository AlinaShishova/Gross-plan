from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap5
from database import get_user_by_username
from werkzeug.security import check_password_hash
from config import Config  
import db_oracle_keys

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_object(Config)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cubs/')
def cubs():
    if 'login' not in session:
        return redirect(url_for('login'))
    return render_template('cubs.html')


@app.route('/order/')
def order():
    if 'login' not in session:
        return redirect(url_for('login'))
    return render_template('order.html')

@app.route('/keys/')
def keys():
    if 'login' not in session:
        return redirect(url_for('login'))
    return render_template('keys.html')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
         # Получаем пользователя из базы данных по имени
        user = get_user_by_username(username)

        if user and check_password_hash(user['password_hash'], password):  # Проверяем пароль
            # Если пароль правильный, сохраняем пользователя в сессии
            session['login'] = user['id']
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('cubs'))  # Перенаправляем на защищенную страницу
        else:
            flash('Неверные имя пользователя или пароль', 'danger')  # Сообщение об ошибке
    
    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def keys():
    # Получаем значение dm_index_where из запроса, по умолчанию 19408746
    dm_index_where = request.args.get('dm_index_where', 19408746, type=int)
    old_dm_index_where = dm_index_where
    
    # Получаем результаты из базы данных с помощью функции из db.py
    results = db_oracle_keys.execute_query(dm_index_where)

    # Рендерим HTML-страницу с результатами
    return render_template('keys.html', results=results, old_dm_index_where=old_dm_index_where)




if __name__ =='__main__':
    app.run(debug=True)
