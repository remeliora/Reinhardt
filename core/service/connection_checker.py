import asyncio
import socket


async def check_device_connection(device, timeout: float = 2.0) -> bool:
    """Проверяет подключение к устройству по TCP"""
    try:
        # Создаем соединение с таймаутом
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(device.ip_address, device.port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (socket.gaierror, ConnectionRefusedError, asyncio.TimeoutError, OSError):
        return False
    except Exception as e:
        # Ловим все остальные исключения
        return False
