from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from infrastructure.db.models.base import Base


class PostgresDB:
    def __init__(
            self,
            url: str,
            pool_size: int = 5,
            max_overflow: int = 10,
            echo: bool = False,
    ):
        """
        url          — строка подключения
        pool_size    — число постоянных соединений в пуле
        max_overflow — сколько дополнительных (в пике) соединений можно создать
        echo         — флаг вывода SQL в лог (для отладки)
        """
        self.engine = create_engine(
            url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def init_db(self) -> None:
        """Создаёт таблицы по моделям, если их ещё нет."""
        from infrastructure.db.models.device import Device
        from infrastructure.db.models.device_type import DeviceType
        from infrastructure.db.models.parameter import Parameter
        from infrastructure.db.models.threshold import Threshold
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Возвращает новую сессию (контекстный менеджер)."""
        return self.SessionLocal()

    def check_connection(self) -> bool:
        """Проверяет, что можно подключиться к БД."""
        try:
            with self.engine.connect():
                return True
        except OperationalError:
            return False