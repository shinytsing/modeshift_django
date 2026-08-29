"""Start a local Django server when needed, then execute the isolated QA suite."""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
ARTIFACTS_DIRECTORY = PROJECT_ROOT / "qa" / "artifacts"


def reset_artifacts() -> None:
    """Rebuild only the gitignored QA evidence directory for a fresh test conclusion."""
    if ARTIFACTS_DIRECTORY.exists():
        shutil.rmtree(ARTIFACTS_DIRECTORY)
    ARTIFACTS_DIRECTORY.mkdir(parents=True, exist_ok=True)


def wait_for_health(base_url: str, timeout_seconds: float = 30) -> None:
    """Fail fast unless the exact API health contract is available."""
    deadline = time.monotonic() + timeout_seconds
    health_url = f"{base_url.rstrip('/')}/health/"
    while time.monotonic() < deadline:
        try:
            with urlopen(health_url, timeout=1) as response:  # nosec B310: controlled QA URL
                if response.status == 200:
                    return
        except (URLError, TimeoutError, OSError):
            time.sleep(0.5)
    raise RuntimeError(f"QA target did not become healthy within {timeout_seconds}s: {health_url}")


def health_is_available(base_url: str) -> bool:
    """Return whether an already-running local target satisfies the health contract."""
    try:
        with urlopen(f"{base_url.rstrip('/')}/health/", timeout=1) as response:  # nosec B310
            return response.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def local_server_address(base_url: str) -> tuple[str, int]:
    """Extract the bind address from a local HTTP base URL."""
    parsed = urlparse(base_url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise ValueError("Set QA_START_SERVER=0 when BASE_URL is not a local HTTP URL.")
    return parsed.hostname, parsed.port or 80


def generate_allure_report() -> None:
    """Render API and UI pytest results into a shareable Allure HTML report."""
    results_directory = ARTIFACTS_DIRECTORY / "allure-results"
    report_directory = ARTIFACTS_DIRECTORY / "allure-report"
    command = ["allure", "generate"]
    if not shutil.which("allure"):
        command = ["npx", "--yes", "allure-commandline@2.34.1", "generate"]

    completed = subprocess.run(
        [*command, str(results_directory), "--clean", "-o", str(report_directory)],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if completed.returncode:
        print("WARNING: Allure HTML report generation failed; pytest artifacts remain available.")


def parse_arguments(arguments: list[str] | None = None) -> list[str]:
    """Return the isolated test directories selected by the command line."""
    parser = ArgumentParser(description="Run QAToolBox shift-left quality checks.")
    selected_suite = parser.add_mutually_exclusive_group()
    selected_suite.add_argument("--api", action="store_true", help="run only requests API contracts")
    selected_suite.add_argument("--ui", action="store_true", help="run only Playwright UI scenarios")
    options = parser.parse_args(arguments)
    if options.api:
        return ["qa/api"]
    if options.ui:
        return ["qa/ui"]
    return ["qa/api", "qa/ui"]


def main(arguments: list[str] | None = None) -> int:
    """Run the same API/UI test command locally and from GitHub Actions."""
    environment = os.environ.copy()
    base_url = environment.setdefault("BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    start_server = environment.get("QA_START_SERVER", "1") == "1"
    server: subprocess.Popen[str] | None = None

    try:
        reset_artifacts()
        if start_server and not health_is_available(base_url):
            host, port = local_server_address(base_url)
            server = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", f"{host}:{port}", "--noreload"],
                cwd=PROJECT_ROOT,
                env=environment,
            )

        wait_for_health(base_url)
        pytest_command = [sys.executable, "-m", "pytest", "-c", "qa/pytest.ini", *parse_arguments(arguments)]
        if environment.get("QA_BROWSER_CHANNEL"):
            pytest_command.extend(["--browser-channel", environment["QA_BROWSER_CHANNEL"]])
        elif sys.platform == "darwin" and Path("/Applications/Google Chrome.app").exists():
            pytest_command.extend(["--browser-channel", "chrome"])

        pytest_result = subprocess.run(
            pytest_command,
            cwd=PROJECT_ROOT,
            env=environment,
            check=False,
        )
        generate_allure_report()
        return pytest_result.returncode
    finally:
        if server and server.poll() is None:
            server.send_signal(signal.SIGTERM)
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
