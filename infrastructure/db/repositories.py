from sqlalchemy.orm import joinedload
from infrastructure.db.models import Device, DeviceType, Parameter, Threshold


class DeviceTypeRepository:
    def __init__(self, session):
        self.session = session

    def get_device_type_by_id(self, device_type_id: int) -> DeviceType:
        """Получение типа устройства по ID с предзагрузкой связанных данных"""
        return self.session.query(DeviceType).options(
            joinedload(DeviceType.parameters),
            joinedload(DeviceType.devices)
        ).filter(DeviceType.id == device_type_id).first()

    def get_all_device_types(self) -> list[DeviceType]:
        """Получение всех типов устройств"""
        return self.session.query(DeviceType).all()


class DeviceRepository:
    def __init__(self, session):
        self.session = session

    def get_device_by_id(self, device_id: int) -> Device:
        """Получение устройства по ID с предзагрузкой связанных данных"""
        return self.session.query(Device).options(
            joinedload(Device.device_type),
            joinedload(Device.thresholds).joinedload(Threshold.parameter)
        ).filter(Device.id == device_id).first()

    def get_devices_by_is_enable_true(self) -> list[Device]:
        """Получение всех активных устройств"""
        return self.session.query(Device).options(
            joinedload(Device.device_type)
        ).filter(Device.is_enable == True).all()

    def get_device_by_ip_and_port(self, ip: str, port: int) -> Device:
        """Поиск устройства по IP и порту"""
        return self.session.query(Device).filter(
            Device.ip_address == ip,
            Device.port == port
        ).first()

    def get_all_devices(self) -> list[Device]:
        """Получение всех устройств"""
        return self.session.query(Device).options(
            joinedload(Device.device_type)
        ).all()


class ParameterRepository:
    def __init__(self, session):
        self.session = session

    def get_parameter_by_id(self, parameter_id: int) -> Parameter:
        """Получение параметра по ID"""
        return self.session.query(Parameter).filter(
            Parameter.id == parameter_id
        ).first()

    def get_parameters_by_device_type(self, device_type_id: int) -> list[Parameter]:
        """Получение параметров по типу устройства"""
        return self.session.query(Parameter).filter(
            Parameter.device_type_id == device_type_id
        ).all()

    def get_all_parameters(self) -> list[Parameter]:
        """Получение всех параметров"""
        return self.session.query(Parameter).all()


class ThresholdRepository:
    def __init__(self, session):
        self.session = session

    def get_threshold_by_id(self, threshold_id: int) -> Threshold:
        """Получение порога по ID"""
        return self.session.query(Threshold).filter(
            Threshold.id == threshold_id
        ).first()

    def get_thresholds_by_parameter_id_and_is_enable_true(
            self,
            parameter_id: int
    ) -> list[Threshold]:
        """Получение активных порогов для параметра"""
        return self.session.query(Threshold).filter(
            Threshold.parameter_id == parameter_id,
            Threshold.is_enable == True
        ).all()

    def get_thresholds_by_device_id(self, device_id: int) -> list[Threshold]:
        """Получение всех порогов для устройства"""
        return self.session.query(Threshold).options(
            joinedload(Threshold.parameter)
        ).filter(Threshold.device_id == device_id).all()

    def get_active_thresholds_by_device_id(
            self,
            device_id: int
    ) -> list[Threshold]:
        """Получение активных порогов для устройства"""
        return self.session.query(Threshold).options(
            joinedload(Threshold.parameter)
        ).filter(
            Threshold.device_id == device_id,
            Threshold.is_enable == True
        ).all()