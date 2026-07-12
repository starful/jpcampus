#!/usr/bin/env python3
"""DEPRECATED: template longtail seed generator.

This script used to emit identical H2 skeletons (Who This Guide Is For, etc.)
which created thin pages later deleted for AdSense quality.

Use scripts/2.generate_ai_guides.py with a curated topics CSV instead.
Set ALLOW_TEMPLATE_LONGTAIL=1 only for emergency debugging (still blocked by quality gates).
"""
from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)


def main() -> None:
    if os.getenv("ALLOW_TEMPLATE_LONGTAIL", "").strip() in {"1", "true", "yes"}:
        print(
            "ALLOW_TEMPLATE_LONGTAIL is set, but template longtail generation "
            "remains disabled after the content-diet cleanup.\n"
            "Use: python scripts/2.generate_ai_guides.py"
        )
        sys.exit(2)

    print(
        "ERROR: scripts/generate_longtail_seed.py is deprecated.\n"
        "It produced identical thin template pages that were removed in the content diet.\n\n"
        "Instead:\n"
        "  1) Add topics to data/guide_topics.csv (unique titles + prompts)\n"
        "  2) Run: python scripts/2.generate_ai_guides.py\n"
        "Quality gates in content_quality.py will reject template heading patterns.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
