import csv
import os
import json
import time
import logging
import glob
import sys
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from common import setup_logging, setup_gemini, clean_json_response, DATA_DIR, CONTENT_DIR, LOG_DIR
from content_quality import (
    GUIDE_QUALITY_PROMPT_RULES,
    assert_quality,
    is_deleted_guide,
)
from topic_queue_csv import resolve as resolve_queue_csv

# --- 설정 ---
setup_logging("guide_gen.log")
model = setup_gemini()

INPUT_CSV = os.path.join(DATA_DIR, "guide_topics.csv")


def _guide_topics_csv() -> str:
    return resolve_queue_csv("guide_topics", INPUT_CSV)
OUTPUT_DIR = CONTENT_DIR
HISTORY_FILE = os.path.join(LOG_DIR, "guide_processed_history.txt")

def _guide_batch_limit() -> int:
    raw = os.getenv("GUIDE_LIMIT", "3").strip()
    try:
        n = int(raw)
    except ValueError:
        n = 3
    return 3 if n <= 0 else n
MAX_WORKERS = 3    # 동시에 작성할 가이드 수 (긴 텍스트 생성이므로 2~4 권장)

THUMBNAILS = {
    "Cost": "https://images.unsplash.com/photo-1561414927-6d86591d0c4f?w=500",
    "Budget": "https://images.unsplash.com/photo-1561414927-6d86591d0c4f?w=500",
    "Selection": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=500",
    "Visa": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500",
    "Housing": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500",
    "Part-time": "https://images.unsplash.com/photo-1556740758-90de374c12ad?w=500",
    "Exam": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500",
    "Preparation": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=500",
    "Settlement": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500",
    "Insurance": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500",
    "Region": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500",
    "default": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=500"
}

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def append_history(slug):
    # 멀티스레드 환경에서 파일 쓰기 시 안전을 위해 간단한 에러 방지
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{slug}\n")

def get_thumbnail(category):
    if not category: return THUMBNAILS["default"]
    for key, url in THUMBNAILS.items():
        if key in category: return url
    return THUMBNAILS["default"]

def generate_content(row):
    # 긴 문장 생성이므로 타임아웃 및 재시도 로직 강화
    prompt = f"""
    You are an expert author who writes comprehensive guides for international students preparing to study in Japan.
    Write a long-form, detailed blog post in **ENGLISH** based on the topic below.
    The article must be well-structured, informative, and easy to read.

    **Total length must be between 7000 and 9000 characters.**

    ---
    Topic Title: {row['title']}
    Core Prompt: {row['prompt']}
    Meta description hint: {row.get('description', '')}
    ---

    Guidelines:
    - Use standard Markdown format.
    - Create 4-7 main sections with clear headings (##) unique to this topic.
    - Use bullet points and lists where appropriate.
    - Maintain a friendly, encouraging, and professional tone in English.
    - Generate ONLY the Markdown body content (do not include frontmatter).

    {GUIDE_QUALITY_PROMPT_RULES}
    """
    for i in range(3):
        try:
            response = model.generate_content(prompt)
            body = clean_json_response(response.text)
            assert_quality(body, kind="guide", require_tables=2)
            return body
        except Exception as e:
            print(f"⚠️ Error details: {e}")  # 에러 내용을 직접 출력해서 확인
            if "429" in str(e):
                time.sleep(30 * (i + 1))  # 대기 시간을 더 늘림 (30초, 60초...)
            else:
                time.sleep(5)
    return None

def process_topic(row):
    """한 개의 주제를 생성하고 파일로 저장하는 단위 작업"""
    slug = row['slug']
    if is_deleted_guide(slug):
        return f"⏭️ Skip deleted slug: {slug}"
    filename = f"guide_{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return f"⏭️ Exists: {filename}"

    content_body = generate_content(row)

    if content_body:
        thumbnail_url = get_thumbnail(row['category'])
        frontmatter_data = {
            "layout": "guide",
            "id": slug,
            "title": row['title'],
            "category": row['category'],
            "tags": [row['category']],
            "description": row['description'],
            "thumbnail": thumbnail_url,
            "date": time.strftime("%Y-%m-%d")
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(json.dumps(frontmatter_data, ensure_ascii=False, indent=2))
            f.write("\n---\n\n")
            f.write(content_body)

        append_history(slug)
        return f"✅ Success: {filename}"
    else:
        return f"❌ Failed: {slug}"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    csv_path = _guide_topics_csv()
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_topics = list(reader)

    processed_slugs = load_history()
    topics_to_process = []
    skipped_deleted = 0
    for row in all_topics:
        slug = (row.get("slug") or "").strip()
        if not slug or slug in processed_slugs:
            continue
        if is_deleted_guide(slug):
            skipped_deleted += 1
            continue
        if os.path.exists(os.path.join(OUTPUT_DIR, f"guide_{slug}.md")):
            continue
        topics_to_process.append(row)
    topics_to_process = topics_to_process[: _guide_batch_limit()]

    print(
        f"🚀 Total: {len(all_topics)} | Processed: {len(processed_slugs)} | "
        f"Pending: {len(topics_to_process)} | Skipped deleted: {skipped_deleted}"
    )
    if not topics_to_process:
        print("✅ No pending guide topics in queue.")
        return

    print(f"⚡ Running with {MAX_WORKERS} workers...")

    failures = 0
    # --- 멀티스레딩 적용 ---
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_topic = {executor.submit(process_topic, row): row for row in topics_to_process}

        for future in tqdm(as_completed(future_to_topic), total=len(topics_to_process)):
            row = future_to_topic[future]
            try:
                result = future.result()
                logging.info(result)
                if result and str(result).startswith("❌"):
                    failures += 1
            except Exception as e:
                failures += 1
                logging.error(f"Error in {row['slug']}: {e}")

    print("\n🎉 Generation finished.")
    if failures:
        print(f"❌ {failures} guide(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()