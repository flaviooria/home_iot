from pydantic import Field, SecretStr

from pydantic_settings import BaseSettings, SettingsConfigDict


class MqttSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    mqtt_broker: str = Field(..., validation_alias="MQTT_BROKER")
    mqtt_port: int = Field(..., validation_alias="MQTT_PORT")
    mqtt_username: str | None = Field(None, validation_alias="MQTT_USERNAME")
    mqtt_password: SecretStr | None = Field(None, validation_alias="MQTT_PASSWORD")
    interval_minutes: int = Field(5, validation_alias="INTERVAL_MINUTES")
    tz: str = Field("Europe/Madrid", validation_alias="TZ")
    config_path: str | None = Field(None, validation_alias="CONFIG_PATH")
    installation_prefix: str | None = Field(None, validation_alias="INSTALLATION_PREFIX")
