import csv
import os
import json
import time
import logging
import glob
from common import setup_logging, setup_gemini, clean_json_response, DATA_DIR, CONTENT_DIR, LOG_DIR

# --- 설정 ---
setup_logging("guide_gen.log")
model = setup_gemini()

INPUT_CSV = os.path.join(DATA_DIR, "guide_topics.csv")
OUTPUT_DIR = CONTENT_DIR
HISTORY_FILE = os.path.join(LOG_DIR, "guide_processed_history.txt")
LIMIT = 5

# 썸네일 설정은 기존과 동일
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
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{slug}\n")

def get_thumbnail(category):
    if not category: return THUMBNAILS["default"]
    for key, url in THUMBNAILS.items():
        if key in category: return url
    return THUMBNAILS["default"]

def generate_content(row):
    print(f"🤖 Generating AI Content (English): {row['title']}...")
    
    # [수정] 영어 콘텐츠 생성 프롬프트
    prompt = f"""
    You are an expert author who writes comprehensive guides for international students preparing to study in Japan.
    Write a long-form, detailed blog post in **ENGLISH** based on the topic below.
    The article must be well-structured, informative, and easy to read.
    
    **Total length must be between 7000 and 8000 characters.**
    
    ---
    Topic Title: {row['title']}
    Core Prompt: {row['prompt']}
    ---
    
    Guidelines: 
    - Use standard Markdown format.
    - Create 3-5 main sections with clear headings (##).
    - Use bullet points and lists where appropriate.
    - Include at least two Markdown tables for comparisons or data.
    - Maintain a friendly, encouraging, and professional tone in English.
    - Generate ONLY the Markdown body content (do not include frontmatter).
    """
    try:
        response = model.generate_content(prompt)
        return clean_json_response(response.text)
    except Exception as e:
        print(f"❌ Error generating {row['slug']}: {e}")
        return None

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ CSV file not found: {INPUT_CSV}")
        return
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_topics = list(reader)

    processed_slugs = load_history()
    topics_to_process = [row for row in all_topics if row['slug'] not in processed_slugs]
    
    print(f"🚀 Total: {len(all_topics)} | Processed: {len(processed_slugs)} | Pending: {len(topics_to_process)}")
    
    count = 0
    for row in topics_to_process:
        if LIMIT > 0 and count >= LIMIT: break

        slug = row['slug']
        filename = f"guide_{slug}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        content_body = generate_content(row)
        
        if content_body:
            thumbnail_url = get_thumbnail(row['category'])
            frontmatter_data = {
                "layout": "guide", 
                "id": slug, 
                "title": row['title'], # CSV의 영문 제목 사용
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
            print(f"✅ Saved: {filename}")
            logging.info(f"Generated: {filename}")
            count += 1
            time.sleep(3)

if __name__ == "__main__":
    main()