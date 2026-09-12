.PHONY: help setup setup-dev setup-rpi test lint up down build ps logs \
	migrate infer-help infer-image infer-camera mqtt-sub mqtt-pub test-backend

MQTT_IMAGE ?= eclipse-mosquitto:2.0.22
HOST ?= localhost
PORT ?= 1883
TOPIC ?= vigi/teste
MODEL_TOPIC ?= vigi/esteira/inspecoes
MANIFEST ?= models/active/manifest.json
CAMERA ?= 0
CAMERA_BACKEND ?= picamera2
UV_RUN ?= uv run --no-sync

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
	@echo "make mqtt-sub                      Escuta mensagens MQTT"
	@echo "make mqtt-pub MSG='mensagem'       Publica uma mensagem MQTT"
	@echo ""
	@echo "Opções: HOST, PORT, TOPIC, MODEL_TOPIC, MANIFEST, CAMERA e CAMERA_BACKEND"

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
	$(UV_RUN) ruff check backend/app backend/migrations edge scripts tests

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
		--mqtt-port "$(PORT)" \
		--mqtt-topic "$(MODEL_TOPIC)"

infer-camera:
	$(UV_RUN) python scripts/infer.py \
		--manifest "$(MANIFEST)" \
		--camera "$(CAMERA)" \
		--backend "$(CAMERA_BACKEND)" \
		--mqtt-host "$(HOST)" \
		--mqtt-port "$(PORT)" \
		--mqtt-topic "$(MODEL_TOPIC)"

mqtt-sub:
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_sub -h $(HOST) -p $(PORT) -t '$(TOPIC)' -v

mqtt-pub:
	@test -n "$(MSG)" || (echo "Informe MSG. Exemplo: make mqtt-pub MSG='Olá MQTT'" && exit 1)
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_pub -h $(HOST) -p $(PORT) -t '$(TOPIC)' -m '$(MSG)'
