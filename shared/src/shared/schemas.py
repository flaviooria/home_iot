from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# Clase base para compartir configuración
class HomeBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- INSTALACIONES ---
class InstallationBase(BaseModel):
    name: str
    topic_prefix: str | None = None
    description: str | None = None


class InstallationCreate(InstallationBase):
    pass  # Lo que recibimos de la API


class Installation(InstallationBase):
    id_item: UUID
    created_at: datetime


# --- ZONAS ---
class ZoneBase(BaseModel):
    name: str
    installation_id: UUID


class ZoneCreate(ZoneBase):
    pass


class Zone(ZoneBase):
    id_item: UUID


# --- DISPOSITIVOS ---
class DeviceBase(BaseModel):
    name: str
    device_type: str
    zone_id: UUID
    topic: str | None = None
    extra_info: dict | None = None


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id_item: UUID
