# scripts/build_data.py

import os
import json
import sys
import frontmatter
from datetime import datetime
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from common import BASE_DIR, CONTENT_DIR  # noqa: E402
from md_dates import ensure_post_date, save_post  # noqa: E402

OUTPUT_DIR = os.path.join(BASE_DIR, 'app', 'static', 'json')
GCS_IMAGE_BASE = os.environ.get(
    "GCS_IMAGE_BASE",
    "https://storage.googleapis.com/ok-project-assets/jpcampus",
)
STAY_THUMB_FALLBACK = "/static/img/logo.png"


def resolve_stay_thumbnail(meta: dict, md_stem: str) -> str:
    raw = str(meta.get("thumbnail") or "").strip()
    if raw.startswith("http") and "unsplash.com" not in raw:
        return raw
    if raw.startswith("/static/images/") or raw.startswith("/static/img/"):
        return f"{GCS_IMAGE_BASE}/{os.path.basename(raw)}"
    if md_stem:
        return f"{GCS_IMAGE_BASE}/{md_stem}.jpg"
    return STAY_THUMB_FALLBACK

def build_json(lang_suffix, output_filename):
    print(f"🔨 Building {output_filename} ...")
    schools_list = []
    backfilled = 0
    
    # 해당 언어의 파일만 찾기 (예: _kr.md 또는 일반 .md)
    all_files = os.listdir(CONTENT_DIR)
    
    # 최신순 정렬
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(CONTENT_DIR, x)), reverse=True)

    for filename in all_files:
        # 학교/대학 파일만 대상
        if not (filename.startswith('univ_') or filename.startswith('school_')):
            continue

        # 언어 필터링 로직
        is_kr_file = filename.endswith('_kr.md')
        
        # 한국어 빌드 중인데 영어 파일이면 스킵
        if lang_suffix == 'kr' and not is_kr_file:
            continue
        # 영어 빌드 중인데 한국어 파일이면 스킵
        if lang_suffix == 'en' and is_kr_file:
            continue

        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                meta = post.metadata

                published_date, changed = ensure_post_date(post, filepath)
                if changed:
                    save_post(filepath, post)
                    backfilled += 1
                
                # ID에서 _kr 제거 (URL은 동일하게 유지하기 위함)
                school_id = meta.get('id').replace('_kr', '') if meta.get('id') else ''
                
                school_data = {
                    "id": school_id,
                    "category": meta.get('category', 'school'),
                    "published": published_date,
                    "basic_info": {
                        "name_ja": meta.get('basic_info', {}).get('name_ja'),
                        "name_en": meta.get('basic_info', {}).get('name_en'),
                        # 한국어 빌드일 경우 name_ko가 있으면 그것을 사용, 없으면 name_en 사용
                        "name_display": meta.get('title'), 
                        "address": meta.get('basic_info', {}).get('address'),
                        "capacity": meta.get('basic_info', {}).get('capacity')
                    },
                    "location": meta.get('location'),
                    "features": meta.get('features', []),
                    "tuition": meta.get('tuition'),
                    "stats": meta.get('stats'),
                    "link": f"/school/{school_id}?lang={lang_suffix}" # 링크에 언어 파라미터 추가
                }
                schools_list.append(school_data)

        except Exception as e:
            print(f"⚠️ Error ({filename}): {e}")

    schools_list.sort(key=lambda x: (x.get('published', ''), x.get('id', '')), reverse=True)

    final_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "schools": schools_list
    }

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False)
    
    print(f"✅ Saved {len(schools_list)} items to {output_filename}")
    if backfilled:
        print(f"📅 date 백필: {backfilled}개 MD")

def build_stays_json(lang_suffix, output_filename):
    print(f"🔨 Building {output_filename} ...")
    stays_list = []

    if not os.path.exists(CONTENT_DIR):
        print("❌ content directory not found")
        return

    for filename in sorted(os.listdir(CONTENT_DIR)):
        if not filename.startswith("stay_"):
            continue
        is_kr_file = filename.endswith("_kr.md")
        if lang_suffix == "kr" and not is_kr_file:
            continue
        if lang_suffix == "en" and is_kr_file:
            continue

        filepath = os.path.join(CONTENT_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
                meta = post.metadata

            stay_id = str(meta.get("id") or "").replace("_kr", "")
            md_stem = stay_id
            if stay_id.startswith("stay_"):
                stay_id = stay_id[5:]
            else:
                md_stem = f"stay_{stay_id}"
            location = meta.get("location") or {}
            rent = meta.get("rent") or {}
            basic = meta.get("basic_info") or {}

            stays_list.append({
                "id": stay_id,
                "entity": "stay",
                "category": "stay",
                "stay_type": meta.get("stay_type", "guesthouse"),
                "published": meta.get("date") or meta.get("published"),
                "basic_info": {
                    "name_en": basic.get("name_en"),
                    "name_ja": basic.get("name_ja"),
                    "name_display": meta.get("title") or basic.get("name_en"),
                    "address": basic.get("address"),
                    "operator": basic.get("operator"),
                },
                "location": location,
                "rent": rent,
                "foreigner_ok": meta.get("foreigner_ok", True),
                "furnished": meta.get("furnished", True),
                "no_guarantor": meta.get("no_guarantor", True),
                "booking_url": meta.get("booking_url", ""),
                "thumbnail": resolve_stay_thumbnail(meta, md_stem),
                "link": f"/stay/{stay_id}?lang={lang_suffix}",
            })
        except Exception as e:
            print(f"⚠️ Stay error ({filename}): {e}")

    stays_list.sort(key=lambda x: (x.get("published", ""), x.get("id", "")), reverse=True)
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "stays": stays_list,
            },
            f,
            ensure_ascii=False,
        )
    print(f"✅ Saved {len(stays_list)} stays to {output_filename}")


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 영어 데이터 빌드 (기본)
    build_json("en", "schools_data.json")

    # 한국어 데이터 빌드
    build_json("kr", "schools_data_kr.json")

    build_stays_json("en", "stays_data.json")
    build_stays_json("kr", "stays_data_kr.json")


if __name__ == "__main__":
    main()