import sys
import asyncio
import logging
from infrastructure.db.postgres import PostgresDB
from core.service.polling_service import PollingService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler("reinhardt_monitor.log")  # Запись в файл
    ]
)


async def main():
    try:
        # Инициализация базы данных
        db = PostgresDB("postgresql://postgres:4803@localhost:5435/reinhardt")
        session = db.get_session()
        logger = logging.getLogger("main")

        # Создаем сервис опроса
        polling_service = PollingService(session)

        # Запускаем сервис опроса
        await polling_service.start()
        logger.info("Сервис опроса успешно запущен")

        # Бесконечный цикл ожидания
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        # Останавливаем сервис при выходе
        if 'polling_service' in locals():
            await polling_service.stop()


if __name__ == "__main__":
    asyncio.run(main())