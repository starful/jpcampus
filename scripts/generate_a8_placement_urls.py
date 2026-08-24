#!/usr/bin/env python3
"""jpcampus wrapper — hub A8 CSV generator (Oakhouse / Cross One Room)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parents[2] / "data" / "a8" / "generate_placement_urls.py"
PROGRAMS = ("oakhouse", "cross_oneroom")


def main() -> None:
    if not HUB.is_file():
        raise SystemExit(f"Hub generator not found: {HUB}")
    args = sys.argv[1:]
    if not args:
        for key in PROGRAMS:
            subprocess.check_call([sys.executable, str(HUB), "--program", key])
        return
    subprocess.check_call([sys.executable, str(HUB), *args])


if __name__ == "__main__":
    main()
