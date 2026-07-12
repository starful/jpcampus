import csv
import json
import os
import re
import sys
import time
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.generativeai.types import GenerationConfig
from common import setup_logging, setup_gemini, clean_json_response, DATA_DIR, CONTENT_DIR, LOG_DIR
from content_quality import (
    ENTITY_QUALITY_PROMPT_RULES,
    assert_quality,
    is_deleted_univ,
)
from topic_queue_csv import resolve as resolve_queue_csv

# --- 설정 ---
setup_logging("univ_gen.log")
model = setup_gemini()

LIMIT = 6
MAX_WORKERS = 5  # 동시에 처리할 개수 (Gemini 유료 계정은 10~20, 무료는 2~5 권장)
INPUT_CSV = os.path.join(DATA_DIR, "univ_list_100.csv")


def _universities_csv() -> str:
    return resolve_queue_csv("universities", INPUT_CSV)
OUTPUT_DIR = CONTENT_DIR
HISTORY_FILE = os.path.join(LOG_DIR, "univ_processed_history.txt")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def append_history(name):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{name}\n")

def get_google_coordinates(address):
    if not address: return {"lat": 35.6812, "lng": 139.7671}
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY, "language": "en"}
    try:
        res = requests.get(base_url, params=params, timeout=5) # 타임아웃 설정
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except: pass
    return {"lat": 35.6812, "lng": 139.7671}

def get_university_info(name_ja, name_en):
    # 멀티스레딩 시 출력이 섞이지 않도록 간단하게 출력
    prompt = f"""
    You are an expert consultant for international students planning to study in Japan.
    Analyze the university "{name_ja}" ({name_en}) and write an in-depth, comprehensive guide in **ENGLISH**.

    Prefer verifiable public facts. If a figure is uncertain, use null or a cautious range —
    do not invent precise enrollment or acceptance numbers.

    Required JSON Structure:
    {{
        "english_slug": "url-friendly-slug-in-english",
        "basic_info": {{
            "name_ja": "{name_ja}",
            "name_en": "{name_en}",
            "address": "Official address (Japanese or English)",
            "website": "Official website URL if known, else empty string",
            "capacity": null
        }},
        "stats": {{
            "international_students": null,
            "acceptance_rate": null
        }},
        "tuition": {{
            "admission_fee": null,
            "yearly_tuition": null
        }},
        "faculties": ["List", "of", "faculties"],
        "features": ["Key Feature 1", "Key Feature 2"],
        "description": "## ...unique markdown body for this university..."
    }}

    description field rules:
    - 5500–8000 characters of Markdown
    - Sections unique to this university (campus location, faculties, admissions path, student life)
    - Include at least one Markdown table (tuition ranges, faculties, or application timeline)
    - Do not use interchangeable boilerplate that could apply to any university unchanged

    {ENTITY_QUALITY_PROMPT_RULES}
    """
    for i in range(3):
        try:
            res = model.generate_content(
                prompt, generation_config=GenerationConfig(response_mime_type="application/json")
            )
            data = json.loads(clean_json_response(res.text))
            body = (data.get("description") or "").strip()
            assert_quality(body, kind="entity", require_tables=1)
            data["description"] = body
            return data
        except Exception as e:
            # 429 Error (Rate Limit) 발생 시 대기 후 재시도
            if "429" in str(e):
                time.sleep(10 * (i + 1))
            else:
                time.sleep(2)
                if i == 2:
                    print(f"⚠️ {name_en} quality/generation error: {e}")
    return None

def process_university(univ):
    """한 대학교를 처리하는 독립적인 작업 단위"""
    name_ja = univ['name_ja']
    name_en = univ['name_en']

    data = get_university_info(name_ja, name_en)
    if not data:
        return f"❌ Failed: {name_ja}"

    addr = data['basic_info'].get('address')
    coords = get_google_coordinates(addr)

    raw_slug = data.get('english_slug', name_en.replace(" ", "-").lower())
    raw_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(raw_slug)).strip("-").lower()
    slug = f"univ_{raw_slug}" if not raw_slug.startswith("univ_") else raw_slug

    if is_deleted_univ(slug):
        return f"⏭️ Skip deleted univ id: {slug}"

    filepath = os.path.join(OUTPUT_DIR, f"{slug}.md")
    if os.path.exists(filepath):
        return f"⏭️ Exists: {slug}.md"

    frontmatter_data = {
        "layout": "school",
        "id": slug,
        "title": data['basic_info']['name_en'],
        "category": "university",
        "tags": data.get('features', []),
        "thumbnail": "/static/img/pin-univ.png",
        "location": coords,
        "basic_info": data['basic_info'],
        "stats": data['stats'],
        "tuition": data['tuition'],
        "faculties": data.get('faculties', []),
        "features": data.get('features', []),
        "date": time.strftime("%Y-%m-%d"),
        "lang": "en",
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(json.dumps(frontmatter_data, ensure_ascii=False, indent=2))
        f.write("\n---\n\n")
        f.write(data.get('description', 'No content available.'))

    append_history(name_ja)
    return f"✅ Saved: {slug}.md"

def main():
    input_csv = _universities_csv()
    if not os.path.exists(input_csv):
        print(f"❌ {input_csv} file not found.")
        sys.exit(1)

    processed_list = load_history()
    univ_list = []
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_ja = (row.get('name_ja') or '').strip()
            if not name_ja or name_ja in processed_list:
                continue
            univ_list.append(row)

    univ_list = univ_list[:LIMIT]  # 처리할 개수 제한
    print(f"🚀 Total Universities to process: {len(univ_list)} | Workers: {MAX_WORKERS}")
    if not univ_list:
        print("✅ No pending universities in queue.")
        return

    failures = 0
    # --- 멀티스레딩 처리 부분 ---
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_univ = {executor.submit(process_university, univ): univ for univ in univ_list}

        for future in tqdm(as_completed(future_to_univ), total=len(univ_list)):
            univ = future_to_univ[future]
            name_ja = univ.get('name_ja', '?')
            try:
                result = future.result()
                if result and str(result).startswith("❌"):
                    failures += 1
            except Exception as e:
                failures += 1
                print(f"⚠️ {name_ja} generated an exception: {e}")

    if failures:
        print(f"❌ {failures} universit(y/ies) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()