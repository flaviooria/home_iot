# Variables
KUBECTL = kubectl
K3S_IP ?= $(shell hostname -I | awk '{print $$1}')
TAG = 0.1.0
IMAGES = home-api home-subscriber home-publisher

.PHONY: help apply delete logs status restart build-images clean k3s-import k3d-import port-forward migrations

help:
	@echo "🏠 Home-IoT Kubernetes Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make apply           - Build images and apply K8s manifests"
	@echo "  make k3s-import     - Save and import images to K3s (containerd)"
	@echo "  make k3d-import     - Import images directly to k3d cluster"
	@echo "  make delete         - Delete all resources"
	@echo "  make status         - Show status of all pods and services"
	@echo "  make logs           - Show logs of all services"
	@echo "  make restart        - Restart all deployments"
	@echo "  make build-images   - Build Docker images locally"
	@echo "  make clean          - Delete all pods (force restart)"
	@echo ""
	@echo "Variables:"
	@echo "  K3S_IP=$(K3S_IP)"
	@echo "  TAG=$(TAG)"

# --- Deployment & Management ---

apply: build-images
	@echo "📦 Applying Kubernetes manifests..."
	@echo "NOTE: Make sure local-path-provisioner is installed!"
	@echo ""
	$(KUBECTL) apply -f k8s/
	@echo ""
	@echo "✅ Apply complete!"
	@echo ""
	@echo "Add this to your /etc/hosts:"
	@echo "$(K3S_IP) home-iot.local"

delete:
	@echo "🗑️  Deleting all resources..."
	$(KUBECTL) delete -f k8s/ --ignore-not-found=true

status:
	@echo "📊 Pods Status:"
	$(KUBECTL) get pods -n home-iot -o wide
	@echo ""
	@echo "📊 Services:"
	$(KUBECTL) get svc -n home-iot
	@echo ""
	@echo "📊 Ingress:"
	$(KUBECTL) get ingress -n home-iot

logs:
	@echo "📝 API Logs:"
	$(KUBECTL) logs -n home-iot -l app=home-api --tail=50
	@echo ""
	@echo "📝 Subscriber Logs:"
	$(KUBECTL) logs -n home-iot -l app=home-subscriber --tail=50
	@echo ""
	@echo "📝 Publisher Logs:"
	$(KUBECTL) logs -n home-iot -l app=home-publisher --tail=50

restart:
	@echo "🔄 Restarting deployments..."
	$(KUBECTL) rollout restart deployment -n home-iot

clean:
	@echo "🧹 Deleting all pods..."
	$(KUBECTL) delete pods --all -n home-iot

# --- Image Handling ---

build-images:
	@echo "🐳 Building Docker images..."
	docker build -t home-api:$(TAG) -f api/Dockerfile .
	docker build -t home-subscriber:$(TAG) -f subscriber/Dockerfile .
	docker build -t home-publisher:$(TAG) -f publisher/Dockerfile .

k3s-import:
	@echo "🚚 Importing images to K3s..."
	@$(foreach img, $(IMAGES), docker save $(img):$(TAG) | sudo k3s ctr images import -;)

k3d-import:
	@echo "🚀 Importing images to k3d..."
	k3d image import $(foreach img, $(IMAGES), $(img):$(TAG)) -c home-iot

# --- Utilities ---

port-forward:
	@echo "🔗 Setting up port forwarding..."
	@echo "API: http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	$(KUBECTL) port-forward -n home-iot svc/home-api 8000:80

migrations:
	@echo "🔧 Running database migrations..."
	$(KUBECTL) exec -n home-iot -it $$(kubectl get pods -n home-iot -l app=home-api -o jsonpath='{.items[0].metadata.name}') -- alembic upgrade head