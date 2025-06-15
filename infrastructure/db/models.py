from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class DeviceType(Base):
    __tablename__ = 'device_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))

    # Отношения
    parameters = relationship("Parameter", back_populates="device_type")
    devices = relationship("Device", back_populates="device_type")


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    ip_address = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    description = Column(String(255))
    is_enable = Column(Boolean, default=True)
    device_type_id = Column(Integer, ForeignKey('device_type.id'), nullable=False)

    # Отношения
    device_type = relationship("DeviceType", back_populates="devices")
    thresholds = relationship("Threshold", back_populates="device")


class Parameter(Base):
    __tablename__ = 'parameter'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    command = Column(String(50), nullable=False)
    metric = Column(String(20))
    description = Column(String(255))
    device_type_id = Column(Integer, ForeignKey('device_type.id'), nullable=False)

    # Отношения
    device_type = relationship("DeviceType", back_populates="parameters")
    thresholds = relationship("Threshold", back_populates="parameter")


class Threshold(Base):
    __tablename__ = 'threshold'

    id = Column(Integer, primary_key=True, autoincrement=True)
    low_value = Column(Float)
    high_value = Column(Float)
    is_enable = Column(Boolean, default=True)
    parameter_id = Column(Integer, ForeignKey('parameter.id'), nullable=False)
    device_id = Column(Integer, ForeignKey('device.id'), nullable=False)

    # Отношения
    parameter = relationship("Parameter", back_populates="thresholds")
    device = relationship("Device", back_populates="thresholds")
