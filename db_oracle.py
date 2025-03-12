import oracledb
from config import Config # Импортируем настройки подключения
from queries import queries # Импортируем словарь с запросами

# Инициализация клиента Oracle
oracle_path= Config.ORACLE_CONFIG["path"]
oracledb.init_oracle_client(lib_dir=oracle_path)


def execute_query(query_name, params=None):
    """ Универсальная функция выполнения SQL-запросов.

    :param query_name: Ключ запроса в словаре queries (например, "keys")
    :param params: Словарь параметров для передачи в SQL (например, {"dm_index_where": 123456})
    :return: Список кортежей с результатами запроса
    """
    results = []

    try:
        # Подключение к базе данных
        connection = oracledb.connect(
        user=Config.ORACLE_CONFIG["user"],
        password=Config.ORACLE_CONFIG["password"],
        dsn=Config.ORACLE_CONFIG["dsn"],)

        cursor = connection.cursor()

        # Получаем SQL-запрос из словаря queries
        sql_query = queries.get(query_name)

        if not sql_query:
            raise ValueError(f"Запрос с ключом '{query_name}' не найден в queries.")

        # Выполнение SQL-запроса с параметрами
        cursor.execute(sql_query, params or {})
        results = cursor.fetchall()

    except Exception as e:
        print(f"Ошибка при выполнении запроса {query_name}: {e}")

    finally:
        # Закрываем соединение с БД
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return results