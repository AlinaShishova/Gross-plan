import oracledb
from config import Config  # Импортируем настройки из config.py

# Инициализация клиента Oracle
oracledb.init_oracle_client(lib_dir="C:/instanclient/instantclient_19_25")

def execute_query(dm_index_where):
    """Функция для выполнения SQL-запроса в Oracle"""
    try:
        # Подключение к базе данных Oracle с использованием настроек из config.py
        connection = oracledb.connect(
            user=Config.ORACLE_CONFIG["user"], 
            password=Config.ORACLE_CONFIG["password"], 
            dsn=Config.ORACLE_CONFIG["dsn"]
        )



        cursor = connection.cursor()

        # SQL-запрос
        query = """
        SELECT d.dm_index,
               d.dm_name as dse_name,
               d.dm_draft as dse_draft_number,
               a.da_num as count_in_assembling,
               a.cn_tech_marshrut as workshop_route,
               (SELECT c.short_name FROM dse_classes c WHERE c.ind = d.dm_class_id) as class_name
        FROM 
            dse_assembling a, 
            dse_main d
        WHERE 
            d.dm_index = a.dm_index_what
            AND a.dm_index_where = :dm_index_where
            AND d.dm_class_id IN (2456, 2454, 2797, 2896)
        ORDER BY 
            d.dm_class_id, 
            d.dm_draft, 
            d.dm_name
        """
        cursor.execute(query, dm_index_where=dm_index_where)
        results = cursor.fetchall()

    finally:
        # Закрываем соединение с базой данных
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return results
