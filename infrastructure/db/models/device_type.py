from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class DeviceType(Base):
    __tablename__ = "device_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))

    parameters = relationship(
        "Parameter",  # Строковое имя класса
        back_populates="device_type"
    )
    devices = relationship(
        "Device",
        back_populates="device_type"
    )

