-- Seed de datos ficticios para home_iot
-- Estructura: 1 instalación → 3 zonas → 6 dispositivos

-- Instalación (topic_prefix debe coincidir con INSTALLATION_PREFIX del ConfigMap)
INSERT INTO installations (id_item, name, topic_prefix, description) VALUES
  ('a0000000-0000-0000-0000-000000000001', 'Casa Principal', 'casa', 'Instalación de prueba')
ON CONFLICT (topic_prefix) DO NOTHING;

-- Zonas
INSERT INTO zones (id_item, name, installation_id) VALUES
  ('b0000000-0000-0000-0000-000000000001', 'Salon',      'a0000000-0000-0000-0000-000000000001'),
  ('b0000000-0000-0000-0000-000000000002', 'Terraza',    'a0000000-0000-0000-0000-000000000001'),
  ('b0000000-0000-0000-0000-000000000003', 'Dormitorio', 'a0000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;

-- Dispositivos (topic = slug que usa el publisher como parte final del topic MQTT)
INSERT INTO devices (id_item, name, device_type, topic, zone_id, extra_info, read_enabled) VALUES
  (
    'c0000000-0000-0000-0000-000000000001',
    'Termómetro Salón', 'temperature_sensor', 'termometro-salon',
    'b0000000-0000-0000-0000-000000000001',
    '{"metrics": ["temperature"], "units": {"temperature": "°C"}}',
    true
  ),
  (
    'c0000000-0000-0000-0000-000000000002',
    'Sensor Humedad Salón', 'soil_moisture_sensor', 'humedad-salon',
    'b0000000-0000-0000-0000-000000000001',
    '{"metrics": ["humidity", "temperature"], "units": {"humidity": "%", "temperature": "°C"}}',
    true
  ),
  (
    'c0000000-0000-0000-0000-000000000003',
    'Termómetro Terraza', 'temperature_sensor', 'termometro-terraza',
    'b0000000-0000-0000-0000-000000000002',
    '{"metrics": ["temperature"], "units": {"temperature": "°C"}}',
    true
  ),
  (
    'c0000000-0000-0000-0000-000000000004',
    'Maceta Inteligente', 'soil_moisture_sensor', 'maceta-terraza',
    'b0000000-0000-0000-0000-000000000002',
    '{"metrics": ["humidity", "temperature"], "units": {"humidity": "%", "temperature": "°C"}}',
    true
  ),
  (
    'c0000000-0000-0000-0000-000000000005',
    'Termómetro Dormitorio', 'temperature_sensor', 'termometro-dormitorio',
    'b0000000-0000-0000-0000-000000000003',
    '{"metrics": ["temperature"], "units": {"temperature": "°C"}}',
    true
  ),
  (
    'c0000000-0000-0000-0000-000000000006',
    'Luz Dormitorio', 'light', 'luz-dormitorio',
    'b0000000-0000-0000-0000-000000000003',
    '{"metrics": ["power"], "units": {"power": "W"}}',
    true
  )
ON CONFLICT (topic) DO NOTHING;

-- Verificación
SELECT i.name AS instalacion, z.name AS zona, d.name AS dispositivo, d.device_type, d.topic
FROM installations i
JOIN zones z ON z.installation_id = i.id_item
JOIN devices d ON d.zone_id = z.id_item
ORDER BY z.name, d.name;
