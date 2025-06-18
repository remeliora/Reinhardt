from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from infrastructure.db.models.device import Device
from infrastructure.db.models.threshold import Threshold
from infrastructure.db.repositories.base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    def __init__(self, session: Session):
        super().__init__(Device, session)

    def get_with_thresholds(self, id: int) -> Optional[Device]:
        """Устройство + тип + все пороги (с параметрами)."""
        return (
            self.session
            .query(Device)
            .options(
                joinedload(Device.device_type),
                joinedload(Device.thresholds).joinedload(Threshold.parameter),
            )
            .filter(Device.id == id)
            .first()
        )

    def list_active(self) -> List[Device]:
        """Все включённые устройства с подгрузкой типа."""
        return (
            self.session
            .query(Device)
            .options(joinedload(Device.device_type))
            .filter(Device.is_enable.is_(True))
            .all()
        )

    def find_by_ip_port(self, ip: str, port: int) -> Optional[Device]:
        """Поиск по IP и порту."""
        return (
            self.session
            .query(Device)
            .filter(Device.ip_address == ip, Device.port == port)
            .first()
        )
