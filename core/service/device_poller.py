import asyncio
import logging
from typing import Dict, List
from infrastructure.db.repositories import ParameterRepository
from core.service.parameter_poller import ParameterPoller
from infrastructure.db.models import Device, Parameter

logger = logging.getLogger("device_poller")


class DevicePoller:
    def __init__(self, device: Device, db_session):
        self.device = device
        self.db_session = db_session
        self.parameters: List[Parameter] = []
        self.parameter_pollers: Dict[int, ParameterPoller] = {}
        self.polling_tasks: Dict[int, asyncio.Task] = {}
        self._is_running = False
        self._task = None

    async def start(self):
        """Запуск опроса устройства"""
        if self._is_running:
            return

        self._is_running = True
        self._task = asyncio.create_task(self._run_device_polling())
        logger.info(f"Опрос устройства {self.device.name} запущен")

    async def stop(self):
        """Остановка опроса устройства"""
        if not self._is_running:
            return

        self._is_running = False

        # Отменяем все активные задачи опроса параметров
        for task in self.polling_tasks.values():
            task.cancel()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"Опрос устройства {self.device.name} остановлен")

    def _load_parameters(self):
        """Загрузка параметров для типа устройства"""
        if not self.parameters:
            param_repo = ParameterRepository(self.db_session)
            self.parameters = param_repo.get_parameters_by_device_type(
                self.device.device_type_id
            )

            # Создаем поллеры для каждого параметра
            for param in self.parameters:
                self.parameter_pollers[param.id] = ParameterPoller(
                    self.device, param
                )

    async def _run_device_polling(self):
        """Основной цикл опроса устройства"""
        while self._is_running:
            try:
                # Загружаем параметры (если еще не загружены)
                self._load_parameters()

                # Запускаем задачи опроса для каждого параметра
                for param_id, poller in self.parameter_pollers.items():
                    if param_id not in self.polling_tasks or self.polling_tasks[param_id].done():
                        self.polling_tasks[param_id] = asyncio.create_task(
                            poller.poll()
                        )

                # Ждем перед следующим циклом опроса
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Ошибка опроса устройства {self.device.name}: {e}")
                await asyncio.sleep(5)