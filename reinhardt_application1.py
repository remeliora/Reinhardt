import asyncio
import logging
import sys

from config import settings
from infrastructure.db.postgres import PostgresDB
from core.service.polling import SensorPollingService


def setup_logging():
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        ],
    )


async def main():
    logger = logging.getLogger("main")

    # 1) Инициализируем БД
    db = PostgresDB(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

    # 2) Передаем фабрику сессий для работы с базой данных
    session_factory = db.get_session

    # 3) Запуск сервиса опроса датчиков
    polling_service = SensorPollingService(session_factory)
    await polling_service.start()


if __name__ == "__main__":
    setup_logging()
    try:
        asyncio.run(main())
    except Exception:
        logging.getLogger("main").exception("Неожиданная ошибка")
        sys.exit(1)
