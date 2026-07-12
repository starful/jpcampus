"""Copy logo placeholder for stays missing app/static/images/stay_*.jpg (GCS rsync target)."""

from __future__ import annotations

import os
import shutil

from common import BASE_DIR, CONTENT_DIR

IMAGES_DIR = os.path.join(BASE_DIR, "app", "static", "images")
IMG_DIR = os.path.join(BASE_DIR, "app", "static", "img")
DEFAULT_CANDIDATES = ("default-stay.png", "logo.png", "default.png", "default.jpg")
PROTECTED = {"logo.png", "logo.svg", "favicon.ico", "og_image.png", "default.png", "default.jpg"}


def _resolve_source() -> str | None:
    for name in DEFAULT_CANDIDATES:
        for base in (IMAGES_DIR, IMG_DIR):
            path = os.path.join(base, name)
            if os.path.isfile(path):
                return path
    return None


def collect_stay_slugs() -> set[str]:
    slugs: set[str] = set()
    if not os.path.isdir(CONTENT_DIR):
        return slugs
    for filename in sorted(os.listdir(CONTENT_DIR)):
        if not filename.startswith("stay_") or not filename.endswith(".md"):
            continue
        if filename.endswith("_kr.md"):
            continue
        slugs.add(filename[:-3])
    return slugs


def ensure_stay_images(*, slugs: set[str] | None = None) -> dict[str, int]:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    targets = sorted(slugs if slugs is not None else collect_stay_slugs())
    copied = skipped = failed = 0

    print(f"\n📋 stay placeholder — {len(targets)} slug(s)\n")

    source = _resolve_source()
    if not source:
        print("  ❌ default image not found (logo.png or default-stay.png)")
        return {"copied": 0, "skipped": 0, "failed": len(targets)}

    for slug in targets:
        if not slug:
            continue
        filename = f"{slug}.jpg"
        if filename in PROTECTED:
            continue
        target = os.path.join(IMAGES_DIR, filename)
        if os.path.isfile(target):
            skipped += 1
            continue
        try:
            shutil.copy2(source, target)
            copied += 1
            print(f"  ✅ {filename} ← {os.path.basename(source)}")
        except OSError as exc:
            failed += 1
            print(f"  ❌ {filename}: {exc}")

    print("\n" + "─" * 50)
    print(f"📋 stay placeholder — copied:{copied} skip:{skipped} fail:{failed}")
    print("─" * 50)
    return {"copied": copied, "skipped": skipped, "failed": failed}


if __name__ == "__main__":
    ensure_stay_images()
