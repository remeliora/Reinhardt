import asyncio
import logging
import re
from infrastructure.db.models import Device, Parameter

logger = logging.getLogger("parameter_poller")


class ParameterPoller:
    def __init__(self, device: Device, parameter: Parameter):
        self.device = device
        self.parameter = parameter
        self._is_polling = False
        self.timeout = 5.0  # Таймаут подключения и чтения
        self.max_retries = 3  # Максимальное количество попыток
        self.retry_delay = 1  # Задержка между попытками

    async def poll(self):
        """Запуск опроса параметра"""
        if self._is_polling:
            return

        self._is_polling = True

        try:
            # Получаем значение параметра с повторными попытками
            value = None
            for attempt in range(self.max_retries):
                try:
                    value = await self._read_parameter_value()
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            f"Попытка {attempt + 1}/{self.max_retries} для параметра {self.parameter.name}: {e}")
                        await asyncio.sleep(self.retry_delay)
                    else:
                        raise

            # Логируем результат
            if value is not None:
                logger.info(
                    f"Устройство {self.device.name} | "
                    f"Параметр {self.parameter.name} ({self.parameter.command}): "
                    f"{value} {self.parameter.metric}"
                )

                # Здесь будет проверка пороговых значений
                # и передача данных в другие системы

        except Exception as e:
            logger.error(f"Ошибка опроса параметра {self.parameter.name}: {e}")
        finally:
            self._is_polling = False

    async def _read_parameter_value(self) -> float:
        """Чтение значения параметра с устройства через TCP-RS232 конвертер"""
        reader, writer = None, None
        try:
            # Устанавливаем соединение с MOXA-конвертером
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    self.device.ip_address,
                    self.device.port
                ),
                timeout=self.timeout
            )

            # Формируем команду для датчика
            command = self._format_command(self.parameter.command)
            writer.write(command.encode())
            await writer.drain()

            # Читаем ответ
            response = await asyncio.wait_for(
                reader.readuntil(b'\r'),  # Ожидаем завершающий символ
                timeout=self.timeout
            )

            # Парсим значение из ответа
            return self._parse_response(response.decode().strip())

        finally:
            # Закрываем соединение
            if writer:
                writer.close()
                await writer.wait_closed()

    def _format_command(self, command: str) -> str:
        """Форматирует команду для отправки на устройство"""
        # Примеры форматов команд:
        # 1. Простая команда: "TE"
        # 2. Команда с параметрами: "M1=ON"
        # 3. Команда с завершающим символом: "DR\r"

        # Добавляем завершающий символ, если его нет
        if not command.endswith('\r'):
            command += '\r'

        return command

    def _parse_response(self, response: str) -> float:
        """Извлекает числовое значение из ответа устройства"""
        # Примеры ответов:
        # 1. Простой ответ: "23.5"
        # 2. Ответ с префиксом: "TEMP=23.5"
        # 3. Ответ с единицами измерения: "23.5 °C"

        # Удаляем нечисловые символы, оставляем только цифры, точки и знаки
        clean_response = re.sub(r'[^\d\.\-]', ' ', response)

        # Ищем числа в очищенной строке
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', clean_response)

        if not numbers:
            raise ValueError(f"Не удалось извлечь число из ответа: '{response}'")

        try:
            # Берем первое найденное число
            return float(numbers[0])
        except ValueError:
            raise ValueError(f"Невозможно преобразовать '{numbers[0]}' в число")