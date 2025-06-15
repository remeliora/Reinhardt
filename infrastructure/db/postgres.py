from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.db.models import Base


class PostgresDB:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_db(self):
        """Создает таблицы, если они не существуют"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Возвращает новый сеанс БД"""
        return self.SessionLocal()

    def check_connection(self):
        """Проверяет подключение к БД"""
        try:
            with self.engine.connect():
                return True
        except Exception:
            return False


# Пример использования при старте приложения
def init_database():
    db = PostgresDB("postgresql://postgres:4803@localhost:5432/reinhardt")

    if not db.check_connection():
        raise ConnectionError("Не удалось подключиться к PostgreSQL")

    db.init_db()
    print("База данных инициализирована")
