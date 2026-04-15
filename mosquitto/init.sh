#!/bin/sh
set -eu

PASSWORD_FILE="/mosquitto/config/pwdfile"
CONFIG_FILE="/mosquitto/config/mosquitto.conf"

: "${MQTT_USERNAME:?MQTT_USERNAME no está definida}"
: "${MQTT_PASSWORD:?MQTT_PASSWORD no está definida}"

mkdir -p "$(dirname "$PASSWORD_FILE")"

if [ ! -f "$PASSWORD_FILE" ]; then
  echo "Creando pwdfile en $PASSWORD_FILE para el usuario $MQTT_USERNAME"
  mosquitto_passwd -b -c "$PASSWORD_FILE" "$MQTT_USERNAME" "$MQTT_PASSWORD"
else
  echo "Actualizando usuario $MQTT_USERNAME"
  mosquitto_passwd -b "$PASSWORD_FILE" "$MQTT_USERNAME" "$MQTT_PASSWORD"
fi

# 🔐 Permisos (importante)
chmod 0700 "$PASSWORD_FILE" || true
chown mosquitto:mosquitto "$PASSWORD_FILE" 2>/dev/null || true

exec mosquitto -c "$CONFIG_FILE"