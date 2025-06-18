import asyncio
import logging
import re
from contextlib import suppress

from infrastructure.db.repositories.repositories import ParameterRepository, ThresholdRepository

logger = logging.getLogger("device_poller")


class DevicePoller:
    def __init__(self, device, db_session, poll_interval: float = 5.0):
        self.device = device
        self.db_session = db_session
        self.interval = poll_interval
        self._is_running = False
        self._task = None

        # Для одного соединения
        self._reader = None
        self._writer = None
        self._conn_lock = asyncio.Lock()

        # Загружаем список параметров один раз
        self.parameters = ParameterRepository(db_session) \
            .get_parameters_by_device_type(device.device_type_id)

    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._run())
        logger.info(f"Опрос {self.device.name} запущен")

    async def stop(self):
        if not self._is_running:
            return
        self._is_running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

        if self._writer:
            self._writer.close()
            with suppress(Exception):
                await self._writer.wait_closed()

        logger.info(f"Опрос {self.device.name} остановлен")

    async def _run(self):
        while self._is_running:
            try:
                # 1) Открываем соединение
                self._reader, self._writer = await asyncio.open_connection(
                    self.device.ip_address, self.device.port
                )

                # 2) Подгружаем все активные пороги для устройства
                thr_repo = ThresholdRepository(self.db_session)
                thresholds = thr_repo.get_active_thresholds_by_device_id(self.device.id)
                # Словарь parameter_id → Threshold
                thr_map = {t.parameter_id: t for t in thresholds}

                # 3) Параллельно опрашиваем параметры (с lock’ом)
                tasks = [
                    asyncio.create_task(self._poll_parameter(param))
                    for param in self.parameters
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 4) Обрабатываем результаты
                for param, res in zip(self.parameters, results):
                    if isinstance(res, Exception):
                        logger.error(f"Ошибка {param.name}: {res}")
                        continue

                    value, metric = res
                    # Поиск порога
                    thr = thr_map.get(param.id)

                    # Определяем статус
                    status = "OK"
                    if thr:
                        if not (thr.low_value <= value <= thr.high_value):
                            status = "ALARM"
                    else:
                        # нет порога — можно залогировать или считать OK
                        logger.debug(f"Порог не найден для {param.name} на {self.device.name}")

                    # Логируем и/или пишем в БД/Firebird
                    logger.info(
                        f"{self.device.name} | {param.name} ({param.command}): "
                        f"{value} {metric} -> {status}"
                    )

                    # здесь же вызвать FirebirdWriter или передать в UI
                    # await self._write_to_firebird(param.id, value, status)

                # 5) Закрываем соединение
                self._writer.close()
                await self._writer.wait_closed()

            except Exception as e:
                logger.error(f"Ошибка цикла опроса {self.device.name}: {e}")

            # 6) Ждём перед следующим циклом
            await asyncio.sleep(self.interval)

    async def _poll_parameter(self, param):
        """Запрос одного параметра через общий сокет + lock."""
        async with self._conn_lock:
            cmd = param.command if param.command.endswith('\r') else param.command + '\r'
            self._writer.write(cmd.encode())
            await self._writer.drain()

            data = await asyncio.wait_for(self._reader.readuntil(b'\r'), timeout=2.0)
            resp = data.decode().strip()

            # небольшая пауза для безопасности
            await asyncio.sleep(0.05)

        val = self._parse_response(resp)
        return val, param.metric

    def _parse_response(self, response: str) -> float:
        clean = re.sub(r'[^\d\.\-]', ' ', response)
        nums = re.findall(r'[-+]?\d*\.\d+|\d+', clean)
        if not nums:
            raise ValueError(f"Не удалось распарсить '{response}'")
        return float(nums[0])
