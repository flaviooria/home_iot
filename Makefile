.PHONY: help apply delete logs status restart build-images clean

KUBECTL = kubectl
K3S_IP ?= $(shell hostname -I | awk '{print $$1}')

help:
	@echo "🏠 Home-IoT Kubernetes Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make apply           - Apply all Kubernetes manifests"
	@echo "  make delete         - Delete all resources"
	@echo "  make status         - Show status of all pods"
	@echo "  make logs           - Show logs of all services"
	@echo "  make restart        - Restart all deployments"
	@echo "  make build-images   - Build Docker images"
	@echo "  make clean          - Delete all pods (force restart)"
	@echo ""
	@echo "Variables:"
	@echo "  K3S_IP=$(K3S_IP)"

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

build-images:
	@echo "🐳 Building Docker images..."
	docker build -t home-api:0.1.0 -f api/Dockerfile .
	docker build -t home-subscriber:0.1.0 -f subscriber/Dockerfile .
	docker build -t home-publisher:0.1.0 -f publisher/Dockerfile .

port-forward:
	@echo "🔗 Setting up port forwarding..."
	@echo "API: http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	$(KUBECTL) port-forward -n home-iot svc/home-api 8000:80

migrations:
	@echo "🔧 Running database migrations..."
	$(KUBECTL) exec -n home-iot -it $$(kubectl get pods -n home-iot -l app=home-api -o jsonpath='{.items[0].metadata.name}') -- alembic upgrade head
