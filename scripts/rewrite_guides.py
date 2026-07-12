#!/usr/bin/env python3
"""Rewrite high-impression guide bodies (EN). Optionally refresh KR via create_korean later."""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
from pathlib import Path

import frontmatter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONTENT_DIR, clean_json_response, setup_gemini, setup_logging  # noqa: E402
from content_quality import GUIDE_QUALITY_PROMPT_RULES, assert_quality  # noqa: E402

setup_logging("guide_rewrite.log")
model = setup_gemini()

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "data" / "content_diet" / "plan.json"

REWRITE_HINTS = {
    "housing": (
        "Target queries: student housing Japan, dormitory/share house for international students, "
        "Tokyo student accommodation. Compare dorm vs share house vs apartment with upfront costs "
        "(shikikin/reikin/agency), monthly rent ranges, guarantor issues, and a clear decision checklist. "
        "Include practical tables. Lead with answer-first summary."
    ),
    "amazon-prime-student": (
        "Focus on Student membership eligibility for international students in Japan, pricing, "
        "what is included, how to verify student status, cancel/renew tips, and whether it is worth it vs free alternatives."
    ),
    "sim-card-guide": (
        "Compare eSIM vs physical SIM vs pocket Wi-Fi for new students: cost, passport requirements, "
        "airport pickup, monthly plans, and a week-1 setup checklist. Include a comparison table."
    ),
    "resume-jp": (
        "Explain Japanese rirekisho vs shokumu-keirekisho for students/baito/job hunting, "
        "required fields, photo rules, common mistakes, and a fill-in checklist. Include example section structure."
    ),
}


def rewrite_one(slug: str) -> str:
    path = Path(CONTENT_DIR) / f"guide_{slug}.md"
    if not path.exists():
        return f"missing:{slug}"

    post = frontmatter.load(str(path))
    meta = dict(post.metadata)
    title = meta.get("title") or slug
    desc = meta.get("description") or ""
    hint = REWRITE_HINTS.get(slug, "Make it uniquely useful and non-generic.")

    prompt = f"""
You are an expert editor for study-in-Japan content on JP Campus.
Rewrite the guide body in ENGLISH as high-quality, original long-form content.

Title: {title}
Existing meta description: {desc}
Editorial brief: {hint}

Rules:
- Output ONLY markdown body (no frontmatter).
- Length 7000–9000 characters.
- Use ## / ### headings, bullet lists, and at least two markdown tables.
- Answer search intent in the first section.
- Practical, specific, 2026-aware. No thin template sections.

{GUIDE_QUALITY_PROMPT_RULES}
""".strip()

    body = None
    last_err = None
    for i in range(3):
        try:
            res = model.generate_content(prompt)
            text = clean_json_response(res.text)
            # if model wrapped in fences already cleaned; ensure markdown
            candidate = text.strip()
            if candidate.startswith("{") and "description" in candidate:
                data = json.loads(candidate)
                candidate = (data.get("description") or "").strip()
            assert_quality(candidate, kind="guide", require_tables=2)
            body = candidate
            break
        except Exception as e:
            last_err = e
            if "429" in str(e):
                time.sleep(20 * (i + 1))
            else:
                time.sleep(3)

    if not body:
        return f"fail:{slug}:{last_err}"

    meta["date"] = date.today().isoformat()
    new_post = frontmatter.Post(body, **meta)
    path.write_text(frontmatter.dumps(new_post) + "\n", encoding="utf-8")

    # Drop stale KR so it can be regenerated separately if needed
    kr = Path(CONTENT_DIR) / f"guide_{slug}_kr.md"
    if kr.exists():
        kr.unlink()
        meta.pop("translated", None)
        new_post = frontmatter.Post(body, **meta)
        path.write_text(frontmatter.dumps(new_post) + "\n", encoding="utf-8")

    return f"ok:{slug}:{len(body)}"


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    slugs = plan.get("rewrite_guides") or list(REWRITE_HINTS)
    print(f"Rewriting {len(slugs)} guides...")
    for slug in slugs:
        print(rewrite_one(slug))


if __name__ == "__main__":
    main()
