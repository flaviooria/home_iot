import asyncio
import json
import socket
import sys
from datetime import datetime, timezone

from aiomqtt import Client, MqttError
from loguru import logger
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from shared.database import engine
from shared.models import Device, Telemetry, Installation

# --- PARCHE WINDOWS ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class SubscriberAgent:
    def __init__(self,
                 mqtt_broker: str,
                 mqtt_port: int,
                 mqtt_username: str | None = None,
                 mqtt_password: SecretStr | None = None):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password

        self.log = logger.bind(service=self.__class__.__name__)
        self.async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

        self.device_map = {}
        self.root_topics = set()

    async def refresh_config_from_db(self):
        """Carga los dispositivos a monitorizar directamente desde Postgres"""
        async with self.async_session() as session:
            # 1. Obtenemos prefijos de instalación
            result_prefixes = await session.execute(select(Installation.topic_prefix))
            # Ajuste para extraer correctamente el string del resultado de la DB
            self.root_topics = {f"{p[0].rstrip('/')}/#" for p in result_prefixes.all() if p[0]}

            # 2. Obtenemos dispositivos habilitados
            stmt = select(Device).where(Device.read_enabled == True)
            result = await session.execute(stmt)
            devices = result.scalars().all()

            self.device_map = {
                d.topic: {
                    "id": d.id_item,
                    "name": d.name,
                    "units": d.extra_info.get("units", {}) if d.extra_info else {}
                } for d in devices
            }
            self.log.info(f"🔄 Configuración DB cargada: {len(self.device_map)} dispositivos.")

    async def _db_save(self, device_id, value, unit, payload):
        async with self.async_session() as session:
            try:
                new_entry = Telemetry(
                    device_id=device_id,
                    value=value,
                    unit=unit,
                    extra_info=payload,
                    created_at=datetime.now(timezone.utc)
                )
                session.add(new_entry)
                await session.commit()
            except Exception as e:
                await session.rollback()
                self.log.error(f"❌ Error al guardar en DB: {e}")

    async def handle_message(self, message):
        """Procesa mensajes con estructura prefijo/zona/dispositivo"""
        full_topic = str(message.topic)

        # Extraemos la última parte (el slug del dispositivo)
        # De "casa-lau-qwet/terraza/sensor-petunias" extrae "sensor-petunias"
        device_topic_slug = full_topic.split('/')[-1]

        # Buscamos en nuestro mapa usando solo esa parte final
        dev = self.device_map.get(device_topic_slug)

        if not dev:
            # Si no lo encontramos, puede que el mapa use el topic completo
            # Intentamos una búsqueda directa por si acaso
            dev = self.device_map.get(full_topic)

        if dev:
            try:
                payload = json.loads(message.payload.decode())
                val = payload.get("value")
                metric = payload.get("metric")
                unit = dev["units"].get(metric, "")

                if val is not None:
                    await self._db_save(dev["id"], float(val), unit, payload)
                    self.log.success(f"📈 [{dev['name']}] {metric}: {val}{unit}")
            except Exception as e:
                self.log.error(f"Error procesando mensaje en {full_topic}: {e}")

    async def run(self):
        """Bucle principal de conexión y escucha"""
        await self.refresh_config_from_db()

        # Preparamos las credenciales
        password = self.mqtt_password.get_secret_value() if isinstance(self.mqtt_password,
                                                                       SecretStr) else self.mqtt_password

        self.log.info(f"Conectando a {self.mqtt_broker}:{self.mqtt_port}...")

        try:
            async with Client(
                    hostname=self.mqtt_broker,
                    port=self.mqtt_port,
                    username=self.mqtt_username,
                    password=password,
                    identifier=f"home_subscriber_{socket.gethostname()}"
            ) as client:
                self.log.success("✅ Conectado al Broker con éxito.")

                # Suscribirse a todos los tópicos raíz
                for t in self.root_topics:
                    await client.subscribe(t)
                    self.log.info(f"📡 Suscrito a: {t}")

                # Escuchar mensajes indefinidamente
                async for message in client.messages:
                    await self.handle_message(message)

        except MqttError as e:
            self.log.error(f"⚠️ Error de MQTT: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)
            await self.run()  # Reintento básico
