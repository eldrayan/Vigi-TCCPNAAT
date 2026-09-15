.PHONY: help setup setup-dev setup-rpi test lint up down build ps logs \
	migrate infer-help infer-image infer-camera preview-camera run-esteira \
	mqtt-sub mqtt-pub test-backend check-env collect collect-headless \
	dvc-login dvc-pull dataset-validate dataset-add dataset-push \
	models-add models-push train-baseline train-tuned calibrate-model \
	evaluate-model promote-model infer-local-image infer-local-camera \
	benchmark-model

MQTT_IMAGE ?= eclipse-mosquitto:2.0.22
HOST ?= localhost
PORT ?= 1883
TOPIC ?= vigi/teste
MANIFEST ?= models/active/manifest.json
CAMERA ?= 0
CAMERA_BACKEND ?= picamera2
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
	@echo "make test                          Executa os testes do Edge"
	@echo "make test-backend                  Executa os testes unitários do backend"
	@echo "make lint                          Verifica o código com Ruff"
	@echo "make up                            Sobe os serviços"
	@echo "make down                          Para os serviços"
	@echo "make build                         Reconstrói o backend"
	@echo "make ps                            Mostra os serviços"
	@echo "make logs                          Acompanha os logs"
	@echo "make migrate                       Executa as migrations"
	@echo "make infer-help                    Mostra as opções do modelo"
	@echo "make infer-image IMAGE=imagem.jpg Executa o modelo e publica no MQTT"
	@echo "make infer-camera                  Captura da câmera e publica no MQTT"
	@echo "make monitor-edge                  Mantém o estado da Raspberry publicado"
	@echo "make preview-camera                Inicia streaming HTTP de preview da câmera na porta 8080"
	@echo "make run-esteira                   Inicia laço contínuo da esteira (sensor + câmera + MQTT)"
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

up:
	docker compose up --build --detach

down:
	docker compose down

build:
	docker compose build backend

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
		mosquitto_sub -h $(HOST) -p $(PORT) -t '$(TOPIC)' -v

mqtt-pub:
	@test -n "$(MSG)" || (echo "Informe MSG. Exemplo: make mqtt-pub MSG='Olá MQTT'" && exit 1)
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_pub -h $(HOST) -p $(PORT) -t '$(TOPIC)' -m '$(MSG)'

GPIO_PIN ?= 17
DEBOUNCE_MS ?= 50
PREVIEW_PORT ?= 8080

preview-camera:
	$(UV_RUN) python scripts/preview_camera.py \
		--backend "$(CAMERA_BACKEND)" \
		--camera-id "$(CAMERA)" \
		--port "$(PREVIEW_PORT)"

run-esteira:
	$(UV_RUN) python scripts/executar_esteira.py \
		--manifest "$(MANIFEST)" \
		--backend "$(CAMERA_BACKEND)" \
		--camera-id "$(CAMERA)" \
		--gpio-pin "$(GPIO_PIN)" \
		--debounce-ms "$(DEBOUNCE_MS)" \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)" \
		--mqtt-topic "$(MODEL_TOPIC)"
