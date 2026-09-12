"""
Descrição: Configura banco temporário e MQTT local para os testes do backend.
Autor: Leôncio Ferreira
"""

import os
import tempfile
from pathlib import Path

test_data_directory = Path(tempfile.mkdtemp(prefix="vigi-tests-"))
os.environ["DATABASE_URL"] = (
    f"sqlite+aiosqlite:///{test_data_directory / 'vigi.db'}"
)
os.environ["MQTT_HOST"] = "127.0.0.1"
os.environ["MQTT_PORT"] = os.getenv("VIGI_TEST_MQTT_PORT", "1883")
os.environ["MQTT_CLIENT_ID"] = "vigi-backend-tests"
