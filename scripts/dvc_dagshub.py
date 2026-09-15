"""Run DVC using the token cached by ``dagshub login``."""

import os
import subprocess
import sys

from dagshub.auth import get_token


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Uso: python scripts/dvc_dagshub.py <comando DVC> [argumentos]",
            file=sys.stderr,
        )
        return 2

    token = get_token(fail_if_no_token=True)
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = token
    env["AWS_SECRET_ACCESS_KEY"] = token
    return subprocess.run(
        [sys.executable, "-m", "dvc", *sys.argv[1:]], env=env, check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
