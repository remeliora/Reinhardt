import asyncio
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from infrastructure.db.repositories.device_repository import DeviceRepository

logger = logging.getLogger("polling_service")


class SensorPollingService:
    def __init__(self, session_factory, update_interval: int = 15):
        """
        session_factory - фабрика сессий для работы с БД
        update_interval - интервал опроса устройств в секундах
        """
        self.session_factory = session_factory
        self.update_interval = update_interval

    async def start(self):
        """Запуск процесса опроса устройств."""
        logger.info("Запуск сервиса опроса устройств.")
        while True:
            await self.poll_devices()  # Асинхронная часть для опроса
            await asyncio.sleep(self.update_interval)

    async def poll_devices(self):
        """Загрузка включенных устройств из базы данных и вывод их информации."""
        # Создаём синхронную сессию для взаимодействия с БД
        session: Session = self.session_factory()

        try:
            # Работаем с базой данных синхронно
            device_repo = DeviceRepository(session)
            active_devices = device_repo.list_active()

            if active_devices:
                logger.info("Список активных устройств:")
                for device in active_devices:
                    logger.info(f"Device Name: {device.name}, IP: {device.ip_address}, Port: {device.port}")
            else:
                logger.info("Нет активных устройств.")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при работе с БД: {e}")

        finally:
            # Закрываем сессию после работы с БД
            session.close()

        # Здесь может быть асинхронная логика опроса данных с устройств
        # Например, проверка подключений к устройствам или их опрос через какой-то внешний сервис.

