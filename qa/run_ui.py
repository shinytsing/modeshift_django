"""Convenience entry point for the Playwright UI quality gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


if __name__ == "__main__":
    runner = Path(__file__).parent / "scripts" / "run_suite.py"
    raise SystemExit(subprocess.run([sys.executable, str(runner), "--ui"], check=False).returncode)
