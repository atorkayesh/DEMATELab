# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Start, stop, and inspect the DEMATELab Docker setups.

Run from anywhere inside the repository:

    uv run scripts/docker.py up               # dev: build, start, open http://localhost:6080
    uv run scripts/docker.py up --prod        # prod: same, using docker-compose-prod.yml
    uv run scripts/docker.py down | restart | logs | status | build | shell  [--prod]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / "DEMATELab" / ".env"
SERVICE = "dematelab"
DEFAULT_PORT = "6080"


class EnvFile:
    """Reads KEY=VALUE pairs from the service's .env file (missing file = no values)."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def exists(self) -> bool:
        return self.path.exists()

    def get(self, key: str) -> str | None:
        if not self.path.exists():
            return None
        for line in self.path.read_text(encoding="utf-8").splitlines():
            name, sep, value = line.strip().partition("=")
            if sep and name.strip() == key:
                return value.strip().strip("'\"") or None
        return None


class DockerCompose:
    """Thin wrapper around `docker compose` for one environment (dev or prod)."""

    def __init__(self, environment: str, env_file: EnvFile) -> None:
        self.environment = environment
        self.env_file = env_file
        self.compose_file = REPO_ROOT / f"docker-compose-{environment}.yml"

    def run(self, *args: str) -> int:
        command = ["docker", "compose", "-f", str(self.compose_file)]
        if self.env_file.exists():
            # Use the service's .env for ${...} interpolation too (e.g. NOVNC_PORT).
            command += ["--env-file", str(self.env_file.path)]
        command += args
        print(f"$ {' '.join(command)}", flush=True)
        return subprocess.call(command, cwd=REPO_ROOT, env=self._environment())

    def url(self) -> str:
        # Same precedence as compose interpolation: shell environment, then .env, then default.
        port = os.environ.get("NOVNC_PORT") or self.env_file.get("NOVNC_PORT") or DEFAULT_PORT
        return f"http://localhost:{port}/"

    def _environment(self) -> dict[str, str]:
        env = dict(os.environ)
        # On Linux, build the image for the host user so bind-mounted exports/ stays writable.
        # Docker Desktop (macOS/Windows) maps ownership itself, so the image default is kept.
        # Values from the shell or .env win (shell variables would otherwise override .env).
        if sys.platform.startswith("linux") and os.getuid() != 0:
            for key, value in (("APP_UID", os.getuid()), ("APP_GID", os.getgid())):
                if key not in env and self.env_file.get(key) is None:
                    env[key] = str(value)
        return env


class DockerCommands:
    """User-facing commands built on DockerCompose."""

    def __init__(self, compose: DockerCompose) -> None:
        self.compose = compose

    def up(self, build: bool, open_browser: bool) -> int:
        if self.compose.environment == "prod" and not self._prod_env_ready():
            return 1
        (REPO_ROOT / "exports").mkdir(exist_ok=True)
        args = ["up", "-d", "--build"] if build else ["up", "-d"]
        code = self.compose.run(*args)
        if code != 0:
            return code
        url = self.compose.url()
        if not self._wait_until_ready(url):
            print(f"DEMATELab did not respond at {url}; check `uv run scripts/docker.py logs`.")
            return 1
        print(f"DEMATELab is running at {url}")
        if open_browser:
            webbrowser.open(url)
        return 0

    def down(self) -> int:
        return self.compose.run("down")

    def restart(self) -> int:
        return self.compose.run("restart", SERVICE)

    def logs(self, follow: bool) -> int:
        return self.compose.run("logs", *(["-f"] if follow else []), SERVICE)

    def status(self) -> int:
        return self.compose.run("ps")

    def build(self) -> int:
        return self.compose.run("build", SERVICE)

    def shell(self) -> int:
        return self.compose.run("exec", SERVICE, "bash")

    def _prod_env_ready(self) -> bool:
        env_file = self.compose.env_file
        if not env_file.exists():
            print("Missing DEMATELab/.env (copy DEMATELab/.env.example to DEMATELab/.env and set VNC_PASSWORD).")
            return False
        password = env_file.get("VNC_PASSWORD")
        if not password:
            print("VNC_PASSWORD is empty in DEMATELab/.env; production requires a password.")
            return False
        if len(password) > 8:
            print("Note: VNC passwords are limited to 8 characters; only the first 8 are checked.")
        return True

    @staticmethod
    def _wait_until_ready(url: str, timeout_seconds: float = 60.0) -> bool:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=2):
                    return True
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                time.sleep(1)
        return False


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage the DEMATELab Docker setups.")
    parser.add_argument(
        "command",
        choices=["up", "down", "restart", "logs", "status", "build", "shell"],
    )
    parser.add_argument("--prod", action="store_true", help="use docker-compose-prod.yml")
    parser.add_argument("--no-build", action="store_true", help="up: skip rebuilding the image")
    parser.add_argument("--no-open", action="store_true", help="up: don't open the browser")
    parser.add_argument("-f", "--follow", action="store_true", help="logs: follow output")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    compose = DockerCompose("prod" if args.prod else "dev", EnvFile(ENV_FILE))
    commands = DockerCommands(compose)
    if args.command == "up":
        return commands.up(build=not args.no_build, open_browser=not args.no_open)
    if args.command == "logs":
        return commands.logs(follow=args.follow)
    return getattr(commands, args.command)()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
