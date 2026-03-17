# Kubernetes (k3s) - Home IoT

Este directorio contiene los manifiestos Kubernetes para desplegar el sistema Home-IoT en un cluster k3s.

---

## 📋 Requisitos Previos

- [k3s](https://k3s.io/) instalado y funcionando
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configurado
- [Docker](https://www.docker.com/) para construir las imágenes
- [local-path-provisioner](https://github.com/rancher/local-path-provisioner) (incluido en k3s por defecto)

---

## 📂 Estructura de Archivos

| Archivo | Descripción |
|---------|-------------|
| `00-namespace-configmap.yaml` | Namespace `home-iot` y ConfigMap con variables de configuración |
| `01-secrets.yaml` | Secrets (credenciales de BD, MQTT) - **⚠️ Cambiar en producción** |
| `10-postgres.yaml` | PostgreSQL 16 como StatefulSet con volumen persistente |
| `11-mqtt.yaml` | Mosquitto MQTT Broker como StatefulSet + ConfigMap |
| `20-api.yaml` | API FastAPI - Deployment (2 réplicas) + Service ClusterIP |
| `21-subscriber.yaml` | Consumidor MQTT - Deployment |
| `22-publisher.yaml` | Publicador de métricas - Deployment |
| `30-ingress.yaml` | Ingress para exponer la API (usa Traefik de k3s) |

---

## 🚀 Instalación

### 1. Verificar que k3s está funcionando

```bash
# Ver nodos
kubectl get nodes

# Ver pods del sistema
kubectl get pods -A
```

### 2. Verificar local-path-provisioner (opcional)

k3s ya incluye local-path-provisioner por defecto. Si no está instalado:

```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
```

Verificar que está corriendo:

```bash
kubectl get pods -n kube-system | grep local-path
```

### 3. Construir las imágenes Docker

```bash
# Opción 1: Usando Makefile
make build-images

# Opción 2: Manual
docker build -t home-api:0.1.0 -f api/Dockerfile .
docker build -t home-subscriber:0.1.0 -f subscriber/Dockerfile .
docker build -t home-publisher:0.1.0 -f publisher/Dockerfile .
```

### 4. Aplicar los manifiestos

```bash
# Opción 1: Usando Makefile
make apply

# Opción 2: Manual
kubectl apply -f k8s/
```

### 5. Configurar el acceso (local)

Agregar la IP de k3s al archivo `/etc/hosts`:

```bash
# Obtener IP del servidor k3s
K3S_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

# Agregar al hosts (requiere sudo)
echo "$K3S_IP home-iot.local" | sudo tee -a /etc/hosts
```

---

## 🔧 Comandos de Uso

### Ver estado

```bash
# Ver todos los pods
kubectl get pods -n home-iot

# Ver con más detalles
kubectl get pods -n home-iot -o wide

# Ver servicios
kubectl get svc -n home-iot

# Ver PVC (volúmenes)
kubectl get pvc -n home-iot

# Estado con Makefile
make status
```

### Ver logs

```bash
# Logs de un servicio específico
kubectl logs -n home-iot -l app=home-api
kubectl logs -n home-iot -l app=home-subscriber
kubectl logs -n home-iot -l app=home-publisher

# Logs en tiempo real
kubectl logs -n home-iot -l app=home-api -f

# Con Makefile
make logs
```

### Reiniciar servicios

```bash
# Reiniciar todos los deployments
kubectl rollout restart deployment -n home-iot

# Reiniciar uno específico
kubectl rollout restart deployment/home-api -n home-iot

# Con Makefile
make restart
```

### Eliminar recursos

```bash
# Eliminar todo
kubectl delete -f k8s/

# Con Makefile
make delete
```

### Acceso a la API

#### Opción 1: Ingress (recomendado para desarrollo local)

```
http://home-iot.local/api/v1/...
http://home-iot.local/docs (Swagger)
```

#### Opción 2: Port-forward

```bash
# Con Makefile
make port-forward

# Manual
kubectl port-forward -n home-iot svc/home-api 8000:80
```

Luego acceder a: `http://localhost:8000`

#### Opción 3: NodePort (alternativo)

Cambiar el Service de ClusterIP a NodePort en `k8s/20-api.yaml`:

```yaml
spec:
  type: NodePort  # Cambiar de ClusterIP a NodePort
  ports:
  - port: 80
    targetPort: 8000
    nodePort: 30080  # Puerto público
```

---

## 🔄 Actualizar Imágenes

Cuando se hace cambios en el código:

```bash
# 1. Reconstruir imágenes
make build-images

# 2. Reiniciar deployments para que usen las nuevas imágenes
kubectl rollout restart deployment -n home-iot

# 3. Verificar
kubectl rollout status deployment/home-api -n home-iot
```

---

## 🧪 Debugging

```bash
# Describir un pod
kubectl describe pod <pod-name> -n home-iot

# Entrar al contenedor
kubectl exec -it <pod-name> -n home-iot -- /bin/sh

# Ver eventos
kubectl get events -n home-iot --sort-by='.lastTimestamp'

# Ver recursos de un deployment
kubectl top pods -n home-iot
```

---

## ⚠️ Notas para Producción (VPS)

### 1. Cambiar credenciales

Editar `k8s/01-secrets.yaml` antes de aplicar:

```yaml
stringData:
  POSTGRES_PASSWORD: "UNA_PASSWORD_FUERTA_AQUI"
  MQTT_PASSWORD: "UNA_PASSWORD_FUERTA_AQUI"
  DATABASE_URL: "postgresql+asyncpg://postgres:UNA_PASSWORD_FUERTA_AQUI@..."
```

### 2. TLS/HTTPS

Instalar [cert-manager](https://cert-manager.io/) y configurar TLS en el Ingress:

```yaml
# 30-ingress.yaml - agregar:
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - home-iot.tudominio.com
    secretName: home-iot-tls
```

### 3. Base de datos gestionada

Para producción, considerar usar:
- **PostgreSQL**: Cloud SQL (GCP), RDS (AWS), Azure Database
- **MQTT**: AWS IoT Core, Azure IoT Hub, EMQX Cloud

### 4. Escalado horizontal

Agregar HPA (HorizontalPodAutoscaler):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: home-api-hpa
  namespace: home-iot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: home-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## 📊 Endpoints Disponibles

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Información del sistema |
| `GET /health` | Health check |
| `GET /api/v1/installations` | Listar instalaciones |
| `GET /api/v1/zones` | Listar zonas |
| `GET /api/v1/devices` | Listar dispositivos |
| `/docs` | Swagger UI |
| `/redoc` | ReDoc |

---

## 🧹 Limpieza

```bash
# Eliminar todo
make delete

# Eliminar volúmenes (¡cuidado! elimina datos)
kubectl delete pvc -n home-iot --all
```

---

## 📝 Makefile

| Comando | Descripción |
|---------|-------------|
| `make apply` | Aplicar todos los manifiestos |
| `make delete` | Eliminar todos los recursos |
| `make status` | Ver estado de pods y servicios |
| `make logs` | Ver logs de todos los servicios |
| `make restart` | Reiniciar todos los deployments |
| `make build-images` | Construir imágenes Docker |
| `make port-forward` | Port-forward a la API |
| `make clean` | Eliminar todos los pods |
| `make migrations` | Ejecutar migraciones de BD |
