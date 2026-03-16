import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, func, Float, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB  # Importamos JSONB explícitamente
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Installation(Base):
    __tablename__ = "installations"
    id_item: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    topic_prefix: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    zones: Mapped[list["Zone"]] = relationship("Zone", back_populates="installation", cascade="all, delete-orphan")


class Zone(Base):
    __tablename__ = "zones"
    id_item: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    installation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("installations.id_item"))
    installation: Mapped["Installation"] = relationship("Installation", back_populates="zones")
    devices: Mapped[list["Device"]] = relationship("Device", back_populates="zone", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"
    id_item: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    zone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("zones.id_item"))

    # SOLUCIÓN: Especificamos JSONB aquí para que resuelva el tipo dict
    extra_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    zone: Mapped["Zone"] = relationship("Zone", back_populates="devices")
    telemetries: Mapped[list["Telemetry"]] = relationship("Telemetry", back_populates="device",
                                                          cascade="all, delete-orphan")

    read_enabled: Mapped[bool] = mapped_column(default=True)  # Activa la lectura de un dispositivo


class Telemetry(Base):
    __tablename__ = "telemetry"
    id_telemetry: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id_item", ondelete="CASCADE"), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(20))

    # SOLUCIÓN: Especificamos JSONB aquí también
    extra_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    device: Mapped["Device"] = relationship("Device", back_populates="telemetries")

    __table_args__ = (
        Index('idx_device_telemetry_time', "device_id", "created_at"),
    )
