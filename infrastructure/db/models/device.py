from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from infrastructure.db.models.base import Base  # общий declarative_base()


class Device(Base):
    __tablename__ = "device"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    ip_address = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    description = Column(String(255))
    is_enable = Column(Boolean, default=True)
    device_type_id = Column(Integer, ForeignKey('device_type.id'), nullable=False)

    device_type = relationship(
        "DeviceType",
        back_populates="devices"
    )
    thresholds = relationship(
        "Threshold",
        back_populates="device",
    )
