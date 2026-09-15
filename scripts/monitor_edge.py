#!/usr/bin/env python3
"""Mantém publicado no MQTT o estado operacional do dispositivo Edge."""

from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.messaging import MQTTDeviceStatusPublisher  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mqtt-host", required=True)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument("--device-id", default=socket.gethostname())
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args(argv)

    if args.interval <= 0:
        parser.error("--interval deve ser maior que zero")

    publisher = MQTTDeviceStatusPublisher(
        host=args.mqtt_host,
        port=args.mqtt_port,
        device_id=args.device_id,
    )
    publisher.start(sensor="ONLINE", camera="ONLINE", processing="ONLINE")
    try:
        while True:
            time.sleep(args.interval)
            publisher.publish(sensor="ONLINE", camera="ONLINE", processing="ONLINE")
    except KeyboardInterrupt:
        publisher.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
