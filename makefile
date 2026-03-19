# Định nghĩa path

VISION_DIR = src/vision-service
RAG_DIR = src/rag-service
API_DIR = src/api-gateway
APP_DIR = mobile/insight_app


.PHONY: help up down dev-services app logs-all
help: ## Hiển thị danh sách các lệnh
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'



up:
	cd infra/docker && docker compose up -d
	cd $(VISION_DIR) && python main.py &
	cd $(RAG_DIR) && python main.py &
	cd $(API_DIR) && ./gradlew bootRun &
	@echo "Tat Ca Service dang khoi dong"

app:
	cd $(APP_DIR) && flutter run -d chrome

dev: up app


down:
	cd infra/docker && docker compose down
	@pkill -f "python main.py" || true
	@pkill -f "./gradlew bootRun" || true
	@echo "Da dung tat cac Service"


status:
	docker ps
	ps aux | grep -E "python main.py|gradlew"

