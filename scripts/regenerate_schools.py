#!/usr/bin/env python3
"""Regenerate language-school markdown bodies from existing frontmatter (real data).

Keeps id/location/courses/features/etc. Replaces only the markdown body.
Reads school ids from data/content_diet/plan.json by default.
"""
from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import frontmatter
from google.generativeai.types import GenerationConfig
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONTENT_DIR, LOG_DIR, clean_json_response, setup_gemini, setup_logging  # noqa: E402

setup_logging("school_regen.log")
model = setup_gemini()

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "data" / "content_diet" / "plan.json"
HISTORY_FILE = Path(LOG_DIR) / "school_regen_history.txt"
MAX_WORKERS = int(os.getenv("SCHOOL_REGEN_WORKERS", "5"))
LIMIT = int(os.getenv("SCHOOL_REGEN_LIMIT", "0"))  # 0 = all


def load_history() -> set[str]:
    if not HISTORY_FILE.exists():
        return set()
    return {line.strip() for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}


def append_history(school_id: str) -> None:
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{school_id}\n")


def build_prompt(meta: dict) -> str:
    bi = meta.get("basic_info") or {}
    name_en = bi.get("name_en") or meta.get("title") or meta.get("id")
    name_ja = bi.get("name_ja") or ""
    address = bi.get("address") or ""
    capacity = bi.get("capacity") or (meta.get("stats") or {}).get("capacity")
    features = meta.get("features") or meta.get("tags") or []
    courses = meta.get("courses") or []
    source = meta.get("source_url") or ""

    courses_txt = json.dumps(courses, ensure_ascii=False, indent=2)[:2500]
    features_txt = ", ".join(str(f) for f in features[:20])

    return f"""
You are an expert advisor for international students choosing Japanese language schools.
Rewrite ONLY the markdown body for this school page in ENGLISH.
Use the REAL DATA below. Do not invent tuition numbers that contradict the course list.
If a fact is missing, say so briefly instead of fabricating precise stats.

School (real data):
- English name: {name_en}
- Japanese name: {name_ja}
- Address: {address}
- Capacity: {capacity}
- Features/tags: {features_txt}
- Source: {source}
- Courses JSON: {courses_txt}

Requirements:
- Output JSON only: {{"description": "markdown body..."}}
- Length 5500–7500 characters in the description field.
- Structure with these H2 sections (emoji ok):
  1) School Overview & Philosophy
  2) Courses, Curriculum & Teaching Style (include a markdown table from course data when available)
  3) Student Body & Campus Life
  4) University & Career Pathways
  5) Practical Tips for Applicants
- Specific to THIS school and city/region when address is known.
- Friendly, practical, non-generic tone. Avoid identical boilerplate across schools.
""".strip()


def regenerate_one(school_id: str) -> str:
    path = Path(CONTENT_DIR) / f"{school_id}.md"
    if not path.exists():
        return f"missing:{school_id}"

    post = frontmatter.load(str(path))
    meta = dict(post.metadata)
    prompt = build_prompt(meta)

    body = None
    for i in range(3):
        try:
            res = model.generate_content(
                prompt,
                generation_config=GenerationConfig(response_mime_type="application/json"),
            )
            data = json.loads(clean_json_response(res.text))
            body = (data.get("description") or "").strip()
            if len(body) >= 2000:
                break
            body = None
        except Exception as e:
            if "429" in str(e):
                time.sleep(15 * (i + 1))
            else:
                time.sleep(3)
                if i == 2:
                    return f"fail:{school_id}:{e}"

    if not body:
        return f"fail:{school_id}:empty"

    meta["date"] = date.today().isoformat()
    meta["lang"] = meta.get("lang") or "en"
    # keep translated flag only if KR file exists
    kr = Path(CONTENT_DIR) / f"{school_id}_kr.md"
    if not kr.exists():
        meta.pop("translated", None)

    new_post = frontmatter.Post(body, **meta)
    path.write_text(frontmatter.dumps(new_post) + "\n", encoding="utf-8")
    append_history(school_id)
    return f"ok:{school_id}:{len(body)}"


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    ids = list(plan.get("regen_schools") or [])
    done = load_history()
    pending = [s for s in ids if s not in done]
    if LIMIT > 0:
        pending = pending[:LIMIT]

    print(f"School regen: {len(pending)} pending / {len(ids)} total | workers={MAX_WORKERS}")
    if not pending:
        print("Nothing to do.")
        return

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(regenerate_one, sid): sid for sid in pending}
        for fut in tqdm(as_completed(futures), total=len(futures)):
            result = fut.result()
            if result.startswith("ok:"):
                ok += 1
            else:
                fail += 1
                print(result)

    print(f"Done. ok={ok} fail={fail}")


if __name__ == "__main__":
    main()
