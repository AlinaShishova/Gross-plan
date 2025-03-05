from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap5
from database import get_user_by_username
from werkzeug.security import check_password_hash
from config import Config  
import db_oracle_keys
from database import connect_db

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


@app.route('/keys/', methods=['GET', 'POST'])
def keys():
    if 'login' not in session:
        return redirect(url_for('login'))
    else:
        # Получаем значение dm_index_where из запроса, по умолчанию 19408746
        dm_index_where = request.args.get('dm_index_where', 19408746, type=int)
        old_dm_index_where = dm_index_where
        
        # Получаем результаты из базы данных с помощью функции из db.py
        results = db_oracle_keys.execute_query(dm_index_where)

        # Рендерим HTML-страницу с результатами
        return render_template('keys.html', results=results, old_dm_index_where=old_dm_index_where)


@app.route('/save_dates', methods=['POST'])
def save_dates():
    data = request.json
    id, name, start_date, end_date = data['assembly_id'], data.get('assembly_name'), data['start_date'], data['end_date']

    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO assembly (assembly_id, assembly_name, start_date, end_date) VALUES (%s,%s, %s, %s) ON CONFLICT (id) DO UPDATE SET start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date", 
                    (id, name, start_date, end_date))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Удаление записи
@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    data = request.json
    id = data['assembly_id']

    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM assembly WHERE assembly_id = %s", (id,))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ =='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
