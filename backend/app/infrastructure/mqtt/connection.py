"""
Descrição: Controla o ciclo de vida da conexão física com o broker MQTT.
Autor: Leôncio Ferreira
"""

import paho.mqtt.client as mqtt

from app.config import Settings


class MQTTConnection:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=settings.mqtt_client_id,
            clean_session=False,
            manual_ack=True,
        )
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    def start(self) -> None:
        self.client.connect_async(
            host=self.settings.mqtt_host,
            port=self.settings.mqtt_port,
        )
        self.client.loop_start()

    def stop(self) -> None:
        self.client.disconnect()
        self.client.loop_stop()

    def is_connected(self) -> bool:
        return self.client.is_connected()
