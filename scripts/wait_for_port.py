from __future__ import annotations

import socket
import sys
import time


def main(host: str, port: int, timeout_seconds: int) -> int:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f"Port {host}:{port} is ready")
                return 0
        except OSError:
            time.sleep(1)
    print(f"Timed out waiting for {host}:{port}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: wait_for_port.py <host> <port> <timeout_seconds>", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])))






