from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from infrastructure.db.models.device_type import DeviceType
from infrastructure.db.repositories.base import BaseRepository


class DeviceTypeRepository(BaseRepository[DeviceType]):
    def __init__(self, session: Session):
        super().__init__(DeviceType, session)

    def get_with_relations(self, id: int) -> Optional[DeviceType]:
        """Получение типа устройства вместе с параметрами и устройствами."""
        return (
            self.session
            .query(DeviceType)
            .options(
                joinedload(DeviceType.parameters),
                joinedload(DeviceType.devices),
            )
            .filter(DeviceType.id == id)
            .first()
        )

    def list_names(self) -> List[str]:
        """Просто список имён всех типов."""
        return [dt.name for dt in self.list_all()]
