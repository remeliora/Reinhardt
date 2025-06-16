import asyncio
import logging
from typing import Dict
from infrastructure.db.repositories import DeviceRepository
from infrastructure.db.models import Device
from core.service.connection_checker import check_device_connection
from core.service.device_poller import DevicePoller

logger = logging.getLogger("polling_service")


class PollingService:
    def __init__(self, db_session, update_interval: int = 60):
        self.db_session = db_session
        self.update_interval = update_interval
        self.active_devices: Dict[int, Device] = {}
        self.device_status: Dict[int, bool] = {}
        self._is_running = False
        self._task = None
        self._connection_tasks: Dict[int, asyncio.Task] = {}
        self._device_pollers: Dict[int, DevicePoller] = {}

    async def start(self):
        if self._is_running:
            return

        self._is_running = True
        self._task = asyncio.create_task(self._run_polling_loop())
        logger.info("Сервис опроса запущен")

    async def stop(self):
        if not self._is_running:
            return

        self._is_running = False

        # Отменяем все активные задачи
        for task in self._connection_tasks.values():
            task.cancel()

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Сервис опроса остановлен")

    async def _run_polling_loop(self):
        while self._is_running:
            try:
                # Получаем список активных устройств
                device_repo = DeviceRepository(self.db_session)
                active_devices = device_repo.get_devices_by_is_enable_true()

                # Обновляем список активных устройств
                current_device_ids = {d.id for d in active_devices}
                self.active_devices = {d.id: d for d in active_devices}

                # Запускаем задачи проверки подключения для новых устройств
                for device_id, device in self.active_devices.items():
                    if device_id not in self._connection_tasks or self._connection_tasks[device_id].done():
                        self._connection_tasks[device_id] = asyncio.create_task(
                            self._monitor_device_connection(device)  # Проверка подключения только один раз
                        )

                # Удаляем задачи для неактивных устройств
                for device_id in list(self._connection_tasks.keys()):
                    if device_id not in current_device_ids:
                        self._connection_tasks[device_id].cancel()
                        del self._connection_tasks[device_id]
                        if device_id in self.device_status:
                            del self.device_status[device_id]

                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Ошибка в основном цикле опроса: {e}")
                await asyncio.sleep(5)

    async def _monitor_device_connection(self, device):
        """Проверка подключения и запуск опроса для каждого устройства"""
        retry_count = 0
        max_retries = 3
        retry_delay = 5

        try:
            is_connected = await check_device_connection(device)  # Проверка подключение к MOXA

            # Обновляем статус устройства
            current_status = self.device_status.get(device.id, None)
            if current_status != is_connected:
                self.device_status[device.id] = is_connected
                status = "Подключено" if is_connected else "Отключено"
                logger.info(f"Устройство {device.name} ({device.ip_address}:{device.port}): {status}")

                # Управляем DevicePoller в зависимости от статуса
                if is_connected:
                    # Создаем и запускаем DevicePoller
                    if device.id not in self._device_pollers:
                        self._device_pollers[device.id] = DevicePoller(device, self.db_session)
                    await self._device_pollers[device.id].start()
                else:
                    # Останавливаем DevicePoller
                    if device.id in self._device_pollers:
                        await self._device_pollers[device.id].stop()

            # Если устройство подключено, то сбрасываем счетчик и ждем перед следующим циклом
            if is_connected:
                retry_count = 0
                await asyncio.sleep(30)  # Ждем некоторое время перед следующим опросом
            else:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.warning(f"Устройство {device.name} недоступно после {max_retries} попыток")
                    if device.id in self._device_pollers:
                        await self._device_pollers[device.id].stop()
                        del self._device_pollers[device.id]
                    # break
                await asyncio.sleep(retry_delay)

        except Exception as e:
            logger.error(f"Ошибка при проверке подключения к {device.name}: {e}")
            await asyncio.sleep(retry_delay)
