import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen


def run_command(name, arguments):
    result = subprocess.run([sys.executable, *arguments], check=False)
    passed = result.returncode == 0
    print(f"{name}: {'PASS' if passed else 'FAIL'}")
    return passed


def start_server(port, database_path):
    environment = os.environ.copy()
    environment["LEDGER_DB_PATH"] = str(database_path)

    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "ledger_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        env=environment,
    )

    deadline = time.monotonic() + 10

    while time.monotonic() < deadline:
        if server.poll() is not None:
            return server, False

        try:
            with socket.create_connection(
                ("127.0.0.1", port), timeout=0.2
            ):
                return server, server.poll() is None
        except OSError:
            time.sleep(0.2)

    return server, False

def main():
    with tempfile.TemporaryDirectory() as output:
        build_ok = run_command(
            "1. Build",
            ["-m", "build", "--outdir", output],
        )

    lint_ok = run_command("2. Lint", ["-m", "ruff", "check", "."])

    tests_ok = run_command("3. Tests", ["-m", "pytest", "-q"])

    server = None
    server_ok = False
    health_ok = False

    with tempfile.TemporaryDirectory() as database_dir:
        database_path = Path(database_dir) / "local-check.sqlite3"

        try:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]

            server, server_ok = start_server(port, database_path)

            if server_ok:
                with urlopen(
                    f"http://127.0.0.1:{port}/health",
                    timeout=5,
                ) as response:
                    health_ok = (
                        response.status == 200
                        and json.load(response) == {"status": "ok"}
                    )

        except (OSError, ValueError) as error:
            print(f"Server or health check failed: {error}")

        finally:
            if server is not None and server.poll() is None:
                server.terminate()

                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()

    print(f"4. Start server: {'PASS' if server_ok else 'FAIL'}")
    print(f"5. Health endpoint: {'PASS' if health_ok else 'FAIL'}")

    passed = all([
        build_ok,
        lint_ok,
        tests_ok,
        server_ok,
        health_ok,
    ])

    print(f"Local check: {'PASS' if passed else 'FAIL'}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())