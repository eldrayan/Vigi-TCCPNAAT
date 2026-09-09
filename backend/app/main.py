"""
Descrição: Inicializa a API FastAPI, suas rotas e a comunicação MQTT.
Autor: Leôncio Ferreira
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.infrastructure.mqtt import MQTTClient, MQTTProducer, MQTTSubscriber
from app.modules.inspections.messaging import InspectionMessageHandler
from app.modules.inspections.routes import router as inspections_router

settings = get_settings()
mqtt_client = MQTTClient(settings)
mqtt_subscriber = MQTTSubscriber(mqtt_client)
mqtt_producer = MQTTProducer(mqtt_client)
mqtt_subscriber.subscribe(
    topic=settings.mqtt_topic_inspections,
    handler=InspectionMessageHandler(),
    qos=settings.mqtt_qos,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mqtt_producer = mqtt_producer
    mqtt_client.start()
    yield
    mqtt_client.stop()


app = FastAPI(
    title="Vigi API",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(inspections_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
