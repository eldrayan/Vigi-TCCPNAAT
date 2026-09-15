#!/usr/bin/env python3
"""Reenvia continuamente as inspeções pendentes da fila local do Edge."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from edge.messaging import (
    InspectionOutbox,
    InspectionOutboxSynchronizer,
    MQTTInspectionPublisher,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mqtt-host", required=True)
    parser.add_argument("--mqtt-port", type=int, default=1883)
    parser.add_argument(
        "--outbox-path",
        type=Path,
        default=Path("data/edge-outbox.db"),
    )
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args(argv)

    if args.interval <= 0:
        parser.error("--interval deve ser maior que zero")

    outbox = InspectionOutbox(args.outbox_path)
    publisher = MQTTInspectionPublisher(args.mqtt_host, args.mqtt_port)
    synchronizer = InspectionOutboxSynchronizer(outbox, publisher)

    publisher.start_session()
    try:
        while True:
            synchronizer.synchronize_once()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    finally:
        publisher.stop_session()


if __name__ == "__main__":
    raise SystemExit(main())
