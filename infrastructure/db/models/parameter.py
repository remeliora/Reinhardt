from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from infrastructure.db.models.base import Base


class Parameter(Base):
    __tablename__ = 'parameter'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    command = Column(String(50), nullable=False)
    metric = Column(String(20))
    description = Column(String(255))
    device_type_id = Column(Integer, ForeignKey('device_type.id'), nullable=False)

    # Указываем строковое имя класса 'DeviceType'
    device_type = relationship(
        "DeviceType",  # Строковое имя класса
        back_populates="parameters"
    )
    thresholds = relationship(
        "Threshold",
        back_populates="parameter"
    )
