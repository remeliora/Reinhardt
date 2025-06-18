from typing import List

from sqlalchemy.orm import Session, joinedload

from infrastructure.db.models.parameter import Parameter
from infrastructure.db.repositories.base import BaseRepository


class ParameterRepository(BaseRepository[Parameter]):
    def __init__(self, session: Session):
        super().__init__(Parameter, session)

    def list_by_device_type(self, device_type_id: int) -> List[Parameter]:
        """Параметры по типу устройства вместе с самим типом."""
        return (
            self.session
            .query(Parameter)
            .options(joinedload(Parameter.device_type))
            .filter(Parameter.device_type_id == device_type_id)
            .all()
        )
