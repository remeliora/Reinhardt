from typing import List

from sqlalchemy.orm import Session, joinedload

from infrastructure.db.models.threshold import Threshold
from infrastructure.db.repositories.base import BaseRepository


class ThresholdRepository(BaseRepository[Threshold]):
    def __init__(self, session: Session):
        super().__init__(Threshold, session)

    def list_by_device(self, device_id: int, only_active: bool = False) -> List[Threshold]:
        """Пороги для устройства; опционально — только активные."""
        q = (
            self.session
            .query(Threshold)
            .options(joinedload(Threshold.parameter))
            .filter(Threshold.device_id == device_id)
        )
        if only_active:
            q = q.filter(Threshold.is_enable.is_(True))
        return q.all()
