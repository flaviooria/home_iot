import asyncio
import sys

from shared.logger import setup_logger
from shared.mqtt_settings import MqttSettings
from src.subscriber import SubscriberAgent

log = setup_logger("Subscriber")


async def start_agent():
    try:
        settings = MqttSettings()  # type: ignore

        subscriber = SubscriberAgent(
            mqtt_broker=settings.mqtt_broker,
            mqtt_port=settings.mqtt_port,
            mqtt_username=settings.mqtt_username,
            mqtt_password=settings.mqtt_password,
        )

        log.info("🚀 Iniciando Subscriber Agent Asíncrono...")

        await subscriber.run()
    except Exception as e:
        log.exception(f"💥 Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(start_agent())
    except KeyboardInterrupt:
        log.info("👋 Agente detenido.")
