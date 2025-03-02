import psycopg2
from werkzeug.security import generate_password_hash
from config import Config  

def connect_db():
    """Создает подключение к PostgreSQL, используя настройки из config.py."""
    try:
        conn = psycopg2.connect(**Config.DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка при подключении к PostgreSQL: {e}")
        raise

def create_user(username, password):
    """Добавляет пользователя в PostgreSQL."""
    hashed_password = generate_password_hash(password)
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (username, hashed_password),
                )
                conn.commit()
                print(f"Пользователь {username} создан!")
    except Exception as e:
        print(f"Ошибка при добавлении пользователя: {e}")

def get_user_by_username(username):
    """Получает пользователя из PostgreSQL по имени."""
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password_hash FROM users WHERE username = %s",
                    ([username])
                )
                result = cursor.fetchone()
                if result:
                    return {"id": result[0], "username": result[1], "password_hash": result[2]}
    except Exception as e:
        print(f"Ошибка при получении пользователя: {e}")
    return None


