# 🏠 Home-IoT Monorepo

¡Bienvenido al sistema de gestión IoT para el hogar! Este proyecto es un **monorepo** profesional basado en Python que
utiliza `uv` para la gestión de dependencias y Docker para el despliegue. Permite monitorizar sensores (humedad,
temperatura) mediante una arquitectura de microservicios robusta y eficiente.

---

## 🏗️ Arquitectura del Sistema

El proyecto utiliza una arquitectura de microservicios donde cada componente tiene una responsabilidad única,
compartiendo lógica mediante un paquete interno.

| Servicio       | Descripción                                        | Tecnología            |
|:---------------|:---------------------------------------------------|:----------------------|
| **API**        | Punto de entrada para el frontend y Grafana.       | FastAPI & Uvicorn     |
| **Subscriber** | Escucha mensajes MQTT y persiste telemetría en DB. | Python & AIOMQTT      |
| **Shared**     | Modelos de SQLAlchemy y utilidades comunes.        | SQLAlchemy & Pydantic |
| **Broker**     | Intercambio de mensajes (Publish/Subscribe).       | Mosquitto (MQTT)      |
| **Database**   | Almacenamiento persistente de datos.               | PostgreSQL 16         |

---

## ⚙️ Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto para centralizar la configuración. Estas variables son consumidas tanto
por Docker como por los scripts locales:

| Variable            | Descripción                                      | Valor Ejemplo                                               |
|:--------------------|:-------------------------------------------------|:------------------------------------------------------------|
| `DATABASE_URL`      | URL de conexión asíncrona                        | `postgresql+asyncpg://postgres:password123@db:5432/home_db` |
| `MQTT_BROKER`       | Host del broker (nombre del servicio en compose) | `broker`                                                    |
| `MQTT_PORT`         | Puerto estándar MQTT                             | `1883`                                                      |
| `POSTGRES_USER`     | Usuario de la base de datos                      | `postgres`                                                  |
| `POSTGRES_PASSWORD` | Contraseña de la base de datos                   | `password123`                                               |

---

## 🚀 Desarrollo en Local

Para trabajar sin Docker, asegúrate de tener instalado [uv](https://docs.astral.sh/uv/).

### 1. Inicialización

```bash
# Instalar todas las dependencias del workspace
uv sync --all-packages
```


### 2. Ejecución de Servicios
Desde la raíz del monorepo, puedes ejecutar cada componente:

- API: `uv run -m fastapi dev api/main.py`

- Subscriber: `uv run python -m subscriber.main`

🐳 Despliegue con Docker Compose
La forma más sencilla de levantar todo el ecosistema (incluyendo base de datos, broker y servicios).


```shell
# Construir imágenes y levantar contenedores en segundo plano
docker compose up -d --build

# Ver logs en tiempo real de la API
docker compose logs -f home-api

# Detener todos los servicios
docker compose down`
```

🗄️ Gestión de Base de Datos (Alembic)
El proyecto utiliza Alembic para las migraciones. Al ser un monorepo, los modelos residen en **_shared/_**, pero las migraciones se controlan desde la raíz:

Crear una nueva migración:
`uv run alembic revision --autogenerate -m "descripcion_del_cambio"`

Aplicar cambios a la base de datos:
`uv run alembic upgrade head`

📂 Estructura del Proyecto
```text
.
├── api/             # Microservicio API (FastAPI)
│   ├── v1/          # Endpoints y lógica de rutas
│   └── main.py      # Punto de entrada de la API
├── subscriber/      # Consumidor de mensajes MQTT
├── publisher/       # Publicador de méticas al broker MQTT
├── shared/          # Modelos de base de datos y esquemas Pydantic
├── pyproject.toml   # Configuración de Workspace de uv
├── uv.lock          # Lockfile de dependencias
└── docker-compose.yml`
```

[!IMPORTANT]
Imports en Monorepo: Debido a la configuración de PYTHONPATH en Docker y uv, usa siempre rutas absolutas partiendo de la raíz:

✅ from shared.models import Telemetry

❌ from ..shared.models import Telemetry

📊 Visualización y Control
- Swagger UI (Documentación API): http://localhost:8000/docs

- Grafana Dashboards: http://localhost:3000 (Admin / Admin)

- MQTT Broker: localhost:1883

Desarrollado con ❤️ para un hogar inteligente.
