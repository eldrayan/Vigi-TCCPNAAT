.PHONY: help up down build ps logs migrate mqtt-sub mqtt-pub

MQTT_IMAGE ?= eclipse-mosquitto:2.0.22
HOST ?= localhost
PORT ?= 1883
TOPIC ?= vigi/teste

help:
	@echo "make up                         Sobe os serviços"
	@echo "make down                       Para os serviços"
	@echo "make build                      Reconstrói o backend"
	@echo "make ps                         Mostra os serviços"
	@echo "make logs                       Acompanha os logs"
	@echo "make migrate                    Executa as migrations"
	@echo "make mqtt-sub                   Escuta mensagens MQTT"
	@echo "make mqtt-pub MSG='mensagem'    Publica uma mensagem MQTT"
	@echo ""
	@echo "Opções: HOST, PORT e TOPIC"

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
	docker compose run --rm --no-deps backend alembic upgrade head

mqtt-sub:
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_sub -h $(HOST) -p $(PORT) -t '$(TOPIC)' -v

mqtt-pub:
	@test -n "$(MSG)" || (echo "Informe MSG. Exemplo: make mqtt-pub MSG='Olá MQTT'" && exit 1)
	docker run --rm --network host $(MQTT_IMAGE) \
		mosquitto_pub -h $(HOST) -p $(PORT) -t '$(TOPIC)' -m '$(MSG)'
