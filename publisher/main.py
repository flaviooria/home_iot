import asyncio
import sys

from shared.logger import setup_logger
from shared.mqtt_settings import MqttSettings
from publisher import PublisherAgent

log = setup_logger("Publisher")


async def start_agent():
    try:
        settings = MqttSettings()  # type: ignore

        agent = PublisherAgent(
            mqtt_broker=settings.mqtt_broker,
            mqtt_port=settings.mqtt_port,
            mqtt_username=settings.mqtt_username,
            mqtt_password=settings.mqtt_password,
            interval_minutes=settings.interval_minutes,
            tz=settings.tz,
            installation_prefix=settings.installation_prefix,
        )

        log.info("🚀 Iniciando Publisher Agent Asíncrono...")
        await agent.run()

    except Exception as e:
        log.exception(f"💥 Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(start_agent())
    except KeyboardInterrupt:
        log.info("👋 Agente detenido.")
