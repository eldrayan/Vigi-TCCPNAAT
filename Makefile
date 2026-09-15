.PHONY: help setup setup-dev setup-rpi configure-env ensure-env model-pull health test lint up down build ps logs \
	backend-up backend-down frontend-up frontend-build edge-up migrate infer-help \
	infer-image infer-camera preview-camera run-conveyor run-esteira monitor-edge sync-outbox mqtt-sub mqtt-pub test-backend \
	check-env collect collect-headless dvc-login dvc-pull dataset-validate dataset-add dataset-push \
	models-add models-push train-baseline train-tuned calibrate-model evaluate-model promote-model \
	infer-local-image infer-local-camera benchmark-model

MQTT_IMAGE ?= eclipse-mosquitto:2.0.22
-include .env
export MQTT_EDGE_USERNAME MQTT_EDGE_PASSWORD
HOST ?= localhost
PORT ?= 1883
TOPIC ?= vigi/teste
MANIFEST ?= models/active/manifest.json
CAMERA ?= 0
CAMERA_BACKEND ?= picamera2
STATION_CODE ?= ESTACAO_01
DEVICE_ID ?= $(STATION_CODE)
BATCH_CODE ?= LOTE_01
GPIO_PIN ?= 17
DEBOUNCE_MS ?= 50
FRONTEND_HOST ?= 0.0.0.0
FRONTEND_PORT ?= 8081
API_URL ?= http://127.0.0.1:8000
UV_RUN ?= uv run --no-sync
DATASET ?= dataset/vigi-cls
MODEL ?= models/candidates/vigi-yolov8n-cls-tuned.pt
BASELINE_CONFIG ?= training_configuration/training-baseline.yaml
TUNED_CONFIG ?= training_configuration/training-tuned.yaml
CALIBRATION_OUTPUT ?= reports/calibration
CALIBRATION_REPORT ?= $(CALIBRATION_OUTPUT)/metrics.json
EVALUATION_OUTPUT ?= reports/model-gate
METRICS ?= $(EVALUATION_OUTPUT)/metrics.json
BENCHMARK_IMAGES ?= $(DATASET)/test
BENCHMARK_RUNS ?= 100
BENCHMARK_WARMUP ?= 10
BENCHMARK_OUTPUT ?= reports/benchmark-pi.json
COLLECT_ARGS ?= --width 1280 --height 720

help:
	@echo "make setup                         Instala as dependências travadas"
	@echo "make setup-dev                     Instala também as ferramentas de desenvolvimento"
	@echo "make setup-rpi                     Instala CPU travado e permite drivers da câmera CSI"
	@echo "make configure-env                 Cria .env com credenciais MQTT locais aleatórias"
	@echo "make model-pull                    Recupera o modelo ativo via DVC"
	@echo "make test                          Executa os testes do Edge"
	@echo "make test-backend                  Executa os testes unitários do backend"
	@echo "make lint                          Verifica o código com Ruff"
	@echo "make up                            Sobe dashboard, API e MQTT em containers"
	@echo "make down                          Para os serviços"
	@echo "make backend-up                    Sobe MQTT, aplica migrations e inicia a API"
	@echo "make backend-down                  Para MQTT e API"
	@echo "make frontend-up                   Inicia o dashboard React na rede local"
	@echo "make frontend-build                Gera o build local do dashboard"
	@echo "make edge-up                       Inicia a Estação 01 com sensor E18-D80NK"
	@echo "make build                         Reconstrói o backend"
	@echo "make ps                            Mostra os serviços"
	@echo "make health                        Consulta a saúde da API"
	@echo "make logs                          Acompanha os logs"
	@echo "make migrate                       Executa as migrations"
	@echo "make infer-help                    Mostra as opções do modelo"
	@echo "make infer-image IMAGE=imagem.jpg Executa o modelo e publica no MQTT"
	@echo "make infer-camera                  Captura da câmera e publica no MQTT"
	@echo "make edge-up                       Executa a Estação 01 pelo sensor E18-D80NK"
	@echo "make monitor-edge                  Mantém o estado da Raspberry publicado"
	@echo "make mqtt-sub                      Escuta mensagens MQTT"
	@echo "make mqtt-pub MSG='mensagem'       Publica uma mensagem MQTT"
	@echo "make sync-outbox                    Reenvia continuamente a fila offline"
	@echo ""
	@echo "Atalhos dos comandos do README:"
	@echo "make check-env                     Verifica o ambiente de treinamento"
	@echo "make collect                       Coleta imagens com a câmera CSI"
	@echo "make collect-headless              Coleta imagens em terminal/SSH"
	@echo "make dvc-login                     Autentica o cliente DagsHub"
	@echo "make dvc-pull                      Baixa os artefatos DVC"
	@echo "make dataset-validate              Valida o dataset"
	@echo "make dataset-add                   Atualiza o ponteiro DVC do dataset"
	@echo "make dataset-push                  Publica o dataset no DagsHub"
	@echo "make models-add                    Atualiza o ponteiro DVC dos modelos"
	@echo "make models-push                   Publica os modelos no DagsHub"
	@echo "make train-baseline                Treina a configuração baseline"
	@echo "make train-tuned                   Treina a configuração ajustada"
	@echo "make calibrate-model               Calibra o limiar no split de validação"
	@echo "make evaluate-model                Avalia o modelo no split de teste"
	@echo "make promote-model                 Promove um modelo aprovado"
	@echo "make infer-local-image IMAGE=...   Executa inferência local em uma imagem"
	@echo "make infer-local-camera            Executa inferência local pela câmera"
	@echo "make benchmark-model               Mede o desempenho do modelo"
	@echo ""
	@echo "Opções gerais: HOST, PORT, TOPIC, MODEL_TOPIC, MANIFEST, CAMERA e CAMERA_BACKEND"
	@echo "Opções MLOps: DATASET, MODEL, METRICS, BENCHMARK_IMAGES, BENCHMARK_RUNS e BENCHMARK_WARMUP"

setup:
	uv sync --frozen --no-dev

setup-dev:
	uv sync --frozen --group dev

setup-rpi:
	@test -d .venv || uv venv --system-site-packages --python /usr/bin/python3 .venv
	uv sync --frozen --no-dev

configure-env:
	@test ! -e .env || (echo ".env já existe; preserve-o ou remova-o conscientemente antes de recriar." && exit 1)
	@cp .env.example .env
	@edge_password=$$(openssl rand -hex 24); backend_password=$$(openssl rand -hex 24); \
		sed -i "s/^MQTT_EDGE_PASSWORD=.*/MQTT_EDGE_PASSWORD=$$edge_password/; s/^MQTT_BACKEND_PASSWORD=.*/MQTT_BACKEND_PASSWORD=$$backend_password/" .env
	@printf "FRONTEND_PORT=$(FRONTEND_PORT)\n" >> .env
	@chmod 600 .env
	@echo ".env criado com credenciais MQTT locais."

ensure-env:
	@test -f .env || $(MAKE) --no-print-directory configure-env

model-pull:
	$(UV_RUN) dvc pull models.dvc
	@test -f "$(MANIFEST)" || (echo "Modelo ativo não encontrado em $(MANIFEST)." && exit 1)

health:
	curl --fail --silent --show-error http://127.0.0.1:8000/health

test:
	$(UV_RUN) pytest -q

test-backend:
	cd backend && uv run --frozen pytest -q

lint:
	$(UV_RUN) ruff check backend/app backend/migrations backend/tests edge scripts tests

check-env:
	$(UV_RUN) python scripts/verificar_ambiente.py

collect:
	python3 scripts/coletar_dataset.py $(COLLECT_ARGS)

collect-headless:
	python3 scripts/coletar_dataset.py --headless $(COLLECT_ARGS)

dvc-login:
	uv run dagshub login

dvc-pull:
	uv run python scripts/dvc_dagshub.py pull "$(DATASET).dvc" models.dvc

dataset-validate:
	$(UV_RUN) python scripts/validar_dataset.py --dataset "$(DATASET)"

dataset-add:
	uv run dvc add "$(DATASET)"

dataset-push:
	uv run python scripts/dvc_dagshub.py push "$(DATASET).dvc"

models-add:
	uv run dvc add models

models-push:
	uv run python scripts/dvc_dagshub.py push models.dvc

train-baseline:
	$(UV_RUN) python scripts/treinar_modelo.py \
		--dataset "$(DATASET)" \
		--config "$(BASELINE_CONFIG)"

train-tuned:
	$(UV_RUN) python scripts/treinar_modelo.py \
		--dataset "$(DATASET)" \
		--config "$(TUNED_CONFIG)"

calibrate-model:
	$(UV_RUN) python scripts/avaliar_modelo.py \
		--model "$(MODEL)" \
		--dataset "$(DATASET)" \
		--calibrate \
		--output "$(CALIBRATION_OUTPUT)"

evaluate-model:
	$(UV_RUN) python scripts/avaliar_modelo.py \
		--model "$(MODEL)" \
		--dataset "$(DATASET)" \
		--calibration-report "$(CALIBRATION_REPORT)" \
		--output "$(EVALUATION_OUTPUT)"

promote-model:
	$(UV_RUN) python scripts/promover_modelo.py \
		--model "$(MODEL)" \
		--metrics "$(METRICS)"

infer-local-image:
	@test -n "$(IMAGE)" || (echo "Informe IMAGE. Exemplo: make infer-local-image IMAGE=imagem.jpg" && exit 1)
	$(UV_RUN) python scripts/infer.py \
		--manifest "$(MANIFEST)" \
		--image "$(IMAGE)"

infer-local-camera:
	$(UV_RUN) python scripts/infer.py \
		--manifest "$(MANIFEST)" \
		--camera "$(CAMERA)" \
		--backend "$(CAMERA_BACKEND)"

benchmark-model:
	$(UV_RUN) python scripts/benchmark_modelo.py \
		--manifest "$(MANIFEST)" \
		--images "$(BENCHMARK_IMAGES)" \
		--runs "$(BENCHMARK_RUNS)" \
		--warmup "$(BENCHMARK_WARMUP)" \
		--output "$(BENCHMARK_OUTPUT)"

up: ensure-env
	docker compose up --build --detach

down:
	docker compose down

backend-up: ensure-env
	docker compose up --build --detach mqtt
	docker compose run --rm --no-deps backend uv run --frozen --no-dev alembic upgrade head
	docker compose up --detach backend

backend-down:
	docker compose down

frontend-up:
	cd frontend && VITE_API_URL="$(API_URL)" npm run dev -- --host "$(FRONTEND_HOST)"

frontend-build:
	cd frontend && npm run build

build:
	docker compose build

ps:
	docker compose ps

logs:
	docker compose logs --follow

migrate:
	docker compose run --rm --no-deps backend uv run --frozen --no-dev alembic upgrade head

infer-help:
	$(UV_RUN) python scripts/infer.py --help

infer-image:
	@test -n "$(IMAGE)" || (echo "Informe IMAGE. Exemplo: make infer-image IMAGE=imagem.jpg" && exit 1)
	$(UV_RUN) python scripts/infer.py \
		--manifest "$(MANIFEST)" \
		--image "$(IMAGE)" \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)"

infer-camera:
	$(UV_RUN) python scripts/infer.py \
		--manifest "$(MANIFEST)" \
		--camera "$(CAMERA)" \
		--backend "$(CAMERA_BACKEND)" \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)"

run-esteira:
	$(UV_RUN) python scripts/executar_esteira.py \
		--manifest "$(MANIFEST)" \
		--backend "$(CAMERA_BACKEND)" \
		--camera-id "$(CAMERA)" \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)" \
		--station-code "$(STATION_CODE)" \
		--batch-code "$(BATCH_CODE)" \
		--gpio-pin "$(GPIO_PIN)" \
		--debounce-ms "$(DEBOUNCE_MS)"

run-conveyor:
	$(UV_RUN) python scripts/run_conveyor.py \
		--manifest "$(MANIFEST)" \
		--backend "$(CAMERA_BACKEND)" \
		--camera "$(CAMERA)" \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)" \
		--station-code "$(STATION_CODE)" \
		--device-id "$(DEVICE_ID)" \
		--batch-code "$(BATCH_CODE)" \
		--gpio-pin "$(GPIO_PIN)" \
		--debounce-ms "$(DEBOUNCE_MS)"

edge-up: run-conveyor

monitor-edge:
	$(UV_RUN) python scripts/monitor_edge.py \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)"

sync-outbox:
	$(UV_RUN) python scripts/sync_outbox.py \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)"

mqtt-sub:
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_sub -h $(HOST) -p $(PORT) \
		-u "$(MQTT_BACKEND_USERNAME)" -P "$(MQTT_BACKEND_PASSWORD)" \
		-t '$(TOPIC)' -v

mqtt-pub:
	@test -n "$(MSG)" || (echo "Informe MSG. Exemplo: make mqtt-pub MSG='Olá MQTT'" && exit 1)
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_pub -h $(HOST) -p $(PORT) \
		-u "$(MQTT_EDGE_USERNAME)" -P "$(MQTT_EDGE_PASSWORD)" \
		-t '$(TOPIC)' -m '$(MSG)'
