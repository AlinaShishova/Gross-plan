import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'

    DB_CONFIG = {
        "dbname": os.environ.get('POSTGRES_DB') or "gross_plan_db",
        "user": os.environ.get('POSTGRES_USER') or "postgres",
        "password": os.environ.get('POSTGRES_PASSWORD') or "secret_password",
        "host": os.environ.get('POSTGRES_HOST') or "localhost",
        "port": int(os.environ.get('POSTGRES_PORT') or 5432),
    }

    ORACLE_CONFIG = {
        "user": os.environ.get('ORACLE_USER') or "oracle_user",
        "password": os.environ.get('ORACLE_PASSWORD') or "oracle_password",
        "dsn": os.environ.get('ORACLE_DSN') or "oracle_host:1521/db1p",
        "database": os.environ.get('ORACLE_DATABASE') or "oracle_db"
    }