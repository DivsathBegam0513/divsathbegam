"""Start both local services, wait for health, and stop both on Ctrl+C."""

import argparse
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent


def port_available(port: int) -> bool:
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def wait_for(url: str, process: subprocess.Popen, seconds: int = 40):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("A service exited during startup. Read the error above.")
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    raise RuntimeError(f"Service did not become ready: {url}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--ui-port", type=int, default=8501)
    args = parser.parse_args()
    if args.api_port == args.ui_port or not all(1 <= p <= 65535 for p in (args.api_port, args.ui_port)):
        parser.error("Choose two different ports between 1 and 65535.")
    for port in [args.api_port, args.ui_port]:
        if not port_available(port):
            parser.error(f"Port {port} is already in use. Stop that service or choose --api-port and --ui-port.")
    # The launcher itself uses only the standard library. Even when invoked by
    # another Python installation, use this project's installed dependencies.
    venv_python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    service_python = str(venv_python) if venv_python.is_file() else sys.executable
    env = os.environ.copy()
    env["BACKEND_URL"] = f"http://127.0.0.1:{args.api_port}"
    env["PYTHONUNBUFFERED"] = "1"
    processes = []
    try:
        api = subprocess.Popen(
            [service_python, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(args.api_port)],
            cwd=ROOT,
            env=env,
        )
        processes.append(api)
        wait_for(env["BACKEND_URL"] + "/health", api)
        ui = subprocess.Popen(
            [
                service_python,
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.address=127.0.0.1",
                f"--server.port={args.ui_port}",
                "--server.headless=true",
            ],
            cwd=ROOT,
            env=env,
        )
        processes.append(ui)
        wait_for(f"http://127.0.0.1:{args.ui_port}/_stcore/health", ui)
        print(
            f"\nLegalEase is ready: http://127.0.0.1:{args.ui_port}\nAPI docs: {env['BACKEND_URL']}/docs\nPress Ctrl+C to stop both services.\n",
            flush=True,
        )
        while all(p.poll() is None for p in processes):
            time.sleep(0.5)
        raise RuntimeError("A service stopped unexpectedly. See its output above.")
    except KeyboardInterrupt:
        print("\nStopping LegalEase…")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
