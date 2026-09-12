"""
Descrição: Inicializa a API FastAPI, suas rotas e a comunicação MQTT.
Autor: Leôncio Ferreira
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.infrastructure.database import engine
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
    try:
        yield
    finally:
        mqtt_client.stop()
        await engine.dispose()


app = FastAPI(
    title="Vigi API",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(inspections_router)


@app.get("/health", tags=["system"])
async def health(response: Response) -> dict[str, str]:
    database_status = "connected"

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        database_status = "disconnected"

    mqtt_status = (
        "connected" if mqtt_client.is_connected() else "disconnected"
    )
    is_healthy = database_status == "connected" and mqtt_status == "connected"

    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": database_status,
        "mqtt": mqtt_status,
    }
