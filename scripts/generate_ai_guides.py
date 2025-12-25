import csv
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# ==========================================
# [설정]
# ==========================================
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

# 경로 설정
INPUT_CSV = "scripts/file/guide_topics.csv"
OUTPUT_DIR = "app/content"
LOG_DIR = "logs"

# 🎯 생성할 가이드 개수 제한 (0 또는 음수면 제한 없음)
LIMIT = 10

# 로깅 설정
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
logging.basicConfig(filename=os.path.join(LOG_DIR, "guide_gen.log"), level=logging.INFO, format='%(asctime)s - %(message)s')

# 🖼️ 카테고리별 썸네일 이미지 매핑 (Unsplash)
THUMBNAILS = {
    "Cost": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=500",       # 돈/계산기
    "Budget": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=500",
    "Selection": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=500",  # 학교/교실
    "Visa": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=500",       # 여권/공항
    "Housing": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500",    # 방/인테리어
    "Part-time": "https://images.unsplash.com/photo-1556740758-90de374c12ad?w=500",     # 카페/알바
    "Exam": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=500",       # 공부/시험
    "Preparation": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=500",# 짐싸기
    "Settlement": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=500", # 스마트폰/은행
    "Insurance": "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500",  # 병원/건강
    "Region": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500",     # 도쿄/도시
    "default": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=500"     # 기본값
}

def get_thumbnail(category):
    """카테고리 문자열에 키워드가 포함되어 있으면 해당 이미지 반환"""
    if not category:
        return THUMBNAILS["default"]
    
    for key, url in THUMBNAILS.items():
        if key in category:
            return url
    return THUMBNAILS["default"]

def generate_content(row):
    print(f"🤖 Generating AI Content for: {row['title']}...")
    
    prompt = f"""
    You are a professional consultant for international students in Japan.
    Write a blog post in **ENGLISH** based on the request below.

    [Topic]
    Title: {row['title']}
    Context: {row['prompt']}

    [Writing Guidelines]
    1. **Format**: Standard Markdown. Use ## for main headings.
    2. **Language**: English Only.
    3. **Tone**: Helpful, informative, encouraging.
    4. **Structure**: Introduction -> 3~4 Key Points -> Summary/Conclusion.
    5. **Tables**: MUST include at least one Markdown table (e.g., Cost comparison, Timeline, Pros/Cons).
    6. **Length**: 1500 ~ 2500 characters.
    7. **Output**: Return ONLY the Markdown body content. Do not include Frontmatter.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error generating {row['slug']}: {e}")
        return None

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ CSV file not found: {INPUT_CSV}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"🚀 Found {len(rows)} topics. Starting generation...")
    
    count = 0
    skipped_count = 0

    for row in rows:
        # 제한 개수 도달 시 중단 (새로 생성한 개수 기준)
        if LIMIT > 0 and count >= LIMIT:
            print(f"🛑 Limit reached ({LIMIT}). Stopping generation.")
            break

        slug = row['slug']
        filename = f"guide_{slug}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # [핵심] 파일 존재 시 스킵
        if os.path.exists(filepath):
            print(f"⏭️ Skipping (Exists): {filename}")
            skipped_count += 1
            logging.info(f"Skipped: {filename}")
            continue

        # AI 콘텐츠 생성
        content_body = generate_content(row)
        
        if content_body:
            # 썸네일 결정
            thumbnail_url = get_thumbnail(row['category'])

            # Frontmatter 구성
            frontmatter = {
                "layout": "guide",
                "id": slug,
                "title": row['title'],
                "category": row['category'],
                "tags": [row['category']],
                "description": row['description'],
                "thumbnail": thumbnail_url,
                "date": time.strftime("%Y-%m-%d")
            }

            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(json.dumps(frontmatter, ensure_ascii=False, indent=2))
                f.write("\n---\n\n")
                f.write(content_body)
            
            print(f"✅ Saved: {filename}")
            logging.info(f"Generated: {filename}")
            count += 1
            time.sleep(2) # API 제한 방지

    print(f"✨ Job Finished. Generated: {count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    main()