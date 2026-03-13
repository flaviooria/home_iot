from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, String, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Installation(Base):
    __tablename__ = "installations"

    id_item: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    topic_prefix: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relación: Una instalación -> muchas zonas
    zones: Mapped[list["Zone"]] = relationship(
        "Zone", back_populates="installation", cascade="all, delete-orphan"
    )


class Zone(Base):
    __tablename__ = "zones"

    id_item: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    installation_id: Mapped[UUID] = mapped_column(ForeignKey("installations.id_item"))

    installation: Mapped["Installation"] = relationship(
        "Installation", back_populates="zones"
    )
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="zone", cascade="all, delete-orphan"
    )


class Device(Base):
    __tablename__ = "devices"

    id_item: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # ej: 'sensor_humedad', 'bombilla_rgb'
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # El topic completo donde publica (ej: house/garden/sensor1)
    topic: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    zone_id: Mapped[UUID] = mapped_column(ForeignKey("zones.id_item"))

    # Aquí guardamos cosas como {"fabricante": "Xiaomi", "version": "1.2"}
    extra_info: Mapped[dict | None] = mapped_column(JSON)

    zone: Mapped["Zone"] = relationship("Zone", back_populates="devices")
