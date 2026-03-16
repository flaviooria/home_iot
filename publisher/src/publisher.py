import asyncio
import json
import random
import sys
from datetime import datetime

from aiomqtt import Client, MqttError
from loguru import logger
from pydantic import SecretStr
from pytz import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from shared.database import engine
from shared.models import Device, Zone

# --- PARCHE WINDOWS ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Sesión para leer la config
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class PublisherAgent:
    def __init__(
            self,
            mqtt_broker: str,
            mqtt_port: int,
            interval_minutes: int,
            tz: str,
            mqtt_username: str | None = None,
            mqtt_password: SecretStr | None = None,
            installation_prefix: str | None = None,
    ):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.interval_seconds = interval_minutes * 60  # Trabajamos en segundos para el sleep
        self.tz = timezone(tz)
        self.installation_prefix = installation_prefix or "default"

        self.log = logger.bind(service=self.__class__.__name__)
        self.devices_data = []

    async def _load_devices_from_db(self):
        """Carga los dispositivos y sus zonas asociadas."""
        async with async_session() as session:
            # Hacemos un join para traer la info de la zona junto al dispositivo
            stmt = (
                select(Device, Zone.name.label("zone_name"))
                .join(Zone, Device.zone_id == Zone.id_item)
                .where(Device.read_enabled == True)
            )
            result = await session.execute(stmt)

            # Guardamos una lista de tuplas o diccionarios con la data necesaria
            for row in result.all():
                device, zone_name = row
                self.devices_data.append({
                    "device": device,
                    "zone_slug": zone_name.lower().replace(" ", "-")  # "Terraza" -> "terraza"
                })

            self.log.info(f"✅ Cargados {len(self.devices_data)} dispositivos con sus zonas.")

    async def publish_all_sensors(self, client: Client) -> None:
        """Publica una ráfaga de datos para todos los dispositivos."""
        if not self.devices_data:
            self.log.warning("No hay dispositivos para simular.")
            return

        for item in self.devices_data:
            device = item["device"]
            zone_slug = item["zone_slug"]

            base_topic = device.topic.lstrip("/")
            full_topic = f"{self.installation_prefix}/{zone_slug}/{base_topic}"

            metrics = device.extra_info.get("metrics", ["value"]) if device.extra_info else ["value"]
            units = device.extra_info.get("units", {}) if device.extra_info else {}

            for metric in metrics:
                payload = {
                    "value": self._generate_value(device.device_type, metric),
                    "metric": metric,
                    "unit": units.get(metric, ""),
                    "timestamp": datetime.now(tz=self.tz).isoformat()
                }

                await client.publish(full_topic, json.dumps(payload), qos=1)
                self.log.info(f"📤 {full_topic} -> {metric}: {payload['value']}")

    @staticmethod
    def _generate_value(device_type: str, metric: str) -> float:
        ranges = {
            "temperature_sensor": {"temperature": (18.0, 27.0)},
            "soil_moisture_sensor": {"humidity": (30.0, 80.0), "temperature": (15.0, 25.0)},
            "light": {"power": (0.0, 5.0)}
        }
        metric_ranges = ranges.get(device_type, {})
        lo, hi = metric_ranges.get(metric, (0.0, 100.0))
        return round(random.uniform(lo, hi), 2)

    async def run(self) -> None:
        """Bucle principal asíncrono."""
        # Cargamos dispositivos antes de conectar
        await self._load_devices_from_db()

        password = self.mqtt_password.get_secret_value() if isinstance(self.mqtt_password,
                                                                       SecretStr) else self.mqtt_password

        while True:
            try:
                async with Client(
                        hostname=self.mqtt_broker,
                        port=self.mqtt_port,
                        username=self.mqtt_username,
                        password=password,
                        identifier="publisher-sim-async"
                ) as client:
                    self.log.success("✅ Conectado al broker MQTT")

                    while True:
                        # Publicamos datos
                        await self.publish_all_sensors(client)

                        # Esperamos al siguiente intervalo
                        self.log.info(f"💤 Durmiendo {self.interval_seconds // 60} min...")
                        await asyncio.sleep(self.interval_seconds)

                        # Opcional: Recargar dispositivos de la DB en cada ciclo
                        # await self._load_devices_from_db()

            except MqttError as e:
                self.log.error(f"⚠️ Error de conexión: {e}. Reintentando en 10s...")
                await asyncio.sleep(10)
