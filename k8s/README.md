# Kubernetes (k3s) — Home IoT

Manifiestos para desplegar el sistema Home-IoT en un clúster k3s local.

---

## Arquitectura

```
                        ┌─────────────────────────────────────────────┐
                        │              Namespace: home-iot             │
                        │                                              │
  Browser / curl  ──▶  Ingress (Traefik)                              │
                        │      │                                       │
                        │      ▼                                       │
                        │   home-api (FastAPI :8000)                   │
                        │      │                                       │
                        │      ▼                                       │
                        │  home-postgres (PostgreSQL :5432) ◀──┐      │
                        │                                       │      │
                        │  home-mqtt (Mosquitto :1883)          │      │
                        │      ▲              │                 │      │
                        │      │              ▼                 │      │
                        │  home-publisher  home-subscriber ─────┘      │
                        │  (publica datos)  (guarda telemetría)        │
                        └─────────────────────────────────────────────┘
```

### Flujo de datos

1. **Publisher** carga dispositivos de PostgreSQL, genera métricas aleatorias y las publica en MQTT (`casa/<zona>/<dispositivo>`) cada 5 minutos.
2. **Subscriber** escucha `casa/#`, recibe los mensajes y persiste la telemetría en PostgreSQL.
3. **API** expone los datos vía REST (FastAPI). Ejecuta migraciones de Alembic al arrancar mediante un init container.

---

## Estructura de manifiestos

| Archivo | Tipo | Descripción |
|---|---|---|
| `00-namespace-configmap.yaml` | Namespace + ConfigMap | Namespace `home-iot` y variables de configuración no sensibles |
| `01-secrets.yaml` | Secret | Credenciales de PostgreSQL, MQTT y DATABASE_URL |
| `10-postgres.yaml` | StatefulSet + Service | PostgreSQL 16, volumen persistente con `local-path` |
| `11-mqtt.yaml` | StatefulSet + Service + ConfigMap | Mosquitto 2.0 con autenticación por contraseña (init container genera el pwdfile) |
| `20-api.yaml` | Deployment + Service | FastAPI, init container ejecuta `alembic upgrade head` antes de arrancar |
| `21-subscriber.yaml` | Deployment | Consumidor MQTT, persiste telemetría en PostgreSQL |
| `22-publisher.yaml` | Deployment | Publica métricas simuladas al broker MQTT |
| `30-ingress.yaml` | Ingress | Expone la API en `http://home-iot.local` vía Traefik |
| `seed.sql` | SQL | Datos de prueba: 1 instalación, 3 zonas, 6 dispositivos |

---

## Requisitos previos

- [k3s](https://k3s.io/) instalado y corriendo (`kubectl get nodes` devuelve un nodo `Ready`)
- [Docker](https://www.docker.com/) para construir las imágenes
- `kubectl` configurado (k3s lo configura automáticamente en `/etc/rancher/k3s/k3s.yaml`)

k3s incluye de serie: Traefik (ingress), local-path-provisioner (almacenamiento) y CoreDNS.

---

## Despliegue desde cero

### 1. Construir las imágenes Docker

Desde la raíz del repositorio:

```bash
make build-images
```

Esto genera:
- `home-api:0.1.0`
- `home-subscriber:0.1.0`
- `home-publisher:0.1.0`

### 2. Importar las imágenes en k3s

k3s usa su propio containerd, **independiente del daemon Docker**. Las imágenes hay que importarlas explícitamente:

```bash
docker save home-api:0.1.0        | sudo k3s ctr images import -
docker save home-subscriber:0.1.0 | sudo k3s ctr images import -
docker save home-publisher:0.1.0  | sudo k3s ctr images import -
```

### 3. Aplicar los manifiestos

```bash
kubectl apply -f k8s/
```

### 4. Verificar que todos los pods arrancan

```bash
kubectl get pods -n home-iot -w
```

Estado esperado (puede tardar 30-60 segundos):

```
NAME                              READY   STATUS    RESTARTS
home-postgres-0                   1/1     Running   0
home-mqtt-0                       1/1     Running   0
home-api-<hash>                   1/1     Running   0
home-publisher-<hash>             1/1     Running   0
home-subscriber-<hash>            1/1     Running   0
```

### 5. Ejecutar la migración inicial

Crea las tablas en PostgreSQL a partir de `migrations/versions/`:

```bash
kubectl exec -n home-iot \
  $(kubectl get pods -n home-iot -l app=home-api -o jsonpath='{.items[0].metadata.name}') \
  -- /app/.venv/bin/alembic upgrade head
```

### 6. Cargar datos de prueba (opcional)

Inserta una instalación, 3 zonas y 6 dispositivos ficticios para que el publisher y subscriber tengan datos con los que operar:

```bash
cat k8s/seed.sql | kubectl exec -i -n home-iot home-postgres-0 -- psql -U postgres -d home_db
```

Después reinicia publisher y subscriber para que carguen los nuevos dispositivos:

```bash
kubectl rollout restart deployment/home-publisher deployment/home-subscriber -n home-iot
```

### 7. Configurar el acceso por dominio

**En Linux / WSL (para acceso desde la propia máquina):**

```bash
echo "$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}') home-iot.local" \
  | sudo tee -a /etc/hosts
```

**En Windows (si el navegador está en Windows con WSL2):**

Abre el Bloc de notas como administrador y edita `C:\Windows\System32\drivers\etc\hosts` añadiendo al final:

```
<IP-del-nodo> home-iot.local
```

Obtén la IP con: `kubectl get nodes -o wide`

Accede en: **`http://home-iot.local`**

---

## Actualizar tras cambios en el código

Cuando se modifica el código de un servicio hay que reconstruir su imagen, reimportarla en k3s y reiniciar el deployment:

```bash
# 1. Reconstruir la imagen del servicio modificado
docker build -t home-api:0.1.0 -f api/Dockerfile .   # o home-subscriber / home-publisher

# 2. Reimportar en k3s
docker save home-api:0.1.0 | sudo k3s ctr images import -

# 3. Aplicar cambios en manifiestos (si los hay)
kubectl apply -f k8s/

# 4. Reiniciar el deployment
kubectl rollout restart deployment/home-api -n home-iot

# 5. Verificar
kubectl rollout status deployment/home-api -n home-iot
```

---

## Comandos de operación

```bash
# Estado general
make status

# Logs en tiempo real
kubectl logs -n home-iot -l app=home-api -f
kubectl logs -n home-iot -l app=home-subscriber -f
kubectl logs -n home-iot -l app=home-publisher -f

# Reiniciar todos los deployments
make restart

# Acceso directo a la API sin configurar hosts
make port-forward          # API en http://localhost:8000

# Ejecutar migraciones manualmente
make migrations

# Eliminar todos los recursos
make delete

# Eliminar también los volúmenes (borra datos)
kubectl delete pvc --all -n home-iot

# Importar imagenes en k3s
make k3s-import

# Importar imagenes en k3d
make k3d-import
```

---

## Endpoints de la API

| Endpoint | Descripción |
|---|---|
| `GET /health` | Health check |
| `GET /` | Bienvenida |
| `GET /api/v1/...` | Endpoints REST |
| `GET /docs` | Swagger UI |
| `GET /redoc` | ReDoc |

---

## Debugging frecuente

```bash
# Ver por qué un pod no arranca
kubectl describe pod <nombre-pod> -n home-iot

# Ver logs del init container de la API
kubectl logs <nombre-pod> -n home-iot -c migrate

# Ver logs del init container de MQTT
kubectl logs <nombre-pod> -n home-iot -c init-passwd

# Ver eventos del namespace
kubectl get events -n home-iot --sort-by='.lastTimestamp'

# Entrar en un contenedor
kubectl exec -it <nombre-pod> -n home-iot -- /bin/sh

# Consultar telemetría directamente en la BD
kubectl exec -n home-iot home-postgres-0 -- \
  psql -U postgres -d home_db \
  -c "SELECT d.name, t.value, t.unit, t.created_at FROM telemetry t JOIN devices d ON d.id_item = t.device_id ORDER BY t.created_at DESC LIMIT 20;"
```

### Problemas conocidos y soluciones

| Síntoma | Causa | Solución |
|---|---|---|
| `home-postgres-0` o `home-mqtt-0` en `Pending` | PVC sin StorageClass | Verificar que `storageClassName: local-path` está en el manifest y que local-path-provisioner corre en `kube-system` |
| `Init:CrashLoopBackOff` en la API | `alembic` no encontrado en PATH | El manifest usa la ruta completa `/app/.venv/bin/alembic`; reconstruir la imagen si el error persiste |
| Subscriber en `0/1 Running` con desconexiones MQTT | Dos pods con el mismo client ID MQTT | Borrar pods duplicados: `kubectl delete pod -n home-iot -l app=home-subscriber` |
| `No module named 'asyncpg'` en la API | El Secret tiene `postgresql+asyncpg://` en lugar de `postgresql+psycopg://` | Verificar `01-secrets.yaml` y reaplicar: `kubectl apply -f k8s/01-secrets.yaml`, luego reiniciar la API |
| `home-iot.local` no resuelve en el navegador Windows | El `/etc/hosts` de WSL no afecta a Windows | Añadir la entrada al hosts de Windows: `C:\Windows\System32\drivers\etc\hosts` |
| Publisher muestra "0 dispositivos" | La BD está vacía o el pod arrancó antes del seed | Cargar el seed y reiniciar: `kubectl rollout restart deployment/home-publisher -n home-iot` |

---

## Notas de seguridad para producción

- Cambiar todas las credenciales en `01-secrets.yaml` antes de desplegar
- El `seed.sql` es solo para desarrollo; no aplicar en producción
- Para TLS, instalar [cert-manager](https://cert-manager.io/) y añadir sección `tls:` en el Ingress junto con el entrypoint `websecure`
- Considerar usar un Secret Store externo (Vault, AWS Secrets Manager) en lugar de Secrets de Kubernetes planos
