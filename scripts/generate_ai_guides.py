import csv
import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import glob

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
HISTORY_FILE = os.path.join(LOG_DIR, "guide_processed_history.txt") # [추가] 처리 기록 파일

LIMIT = 3

# 로깅 및 기록 파일 디렉토리 생성
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
logging.basicConfig(filename=os.path.join(LOG_DIR, "guide_gen.log"), level=logging.INFO, format='%(asctime)s - %(message)s')

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

# [추가] 기록 관련 함수
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
    print(f"🤖 Generating AI Content for: {row['title']}...")
    prompt = f"""
    You are an expert author who writes comprehensive guides for international students preparing to study in Japan.
    Write a long-form, detailed blog post in **ENGLISH** based on the topic below.
    The article must be well-structured, informative, and easy to read.
    **Total length must be between 7000 and 8000 characters.**
    ---
    ### Topic Details ###
    **Title:** {row['title']}
    **Core Prompt:** {row['prompt']}
    ---
    ### Writing Guidelines & Structure ###
    1.  **Format:** Use standard Markdown. Use `##` for main headings and `###` for subheadings.
    2.  **Introduction:** Start with an engaging introduction that explains why this topic is important for students.
    3.  **Main Body:**
        -   Break down the topic into 3-5 logical main sections using `##` headings.
        -   Under each main section, use `###` subheadings to provide more detailed points.
        -   Use bullet points (`-`) or numbered lists (`1.`) for clarity.
        -   **Include at least two detailed Markdown tables.** For example, comparison tables (Tokyo vs. Osaka), cost breakdown tables, pros and cons, or timelines. Tables are crucial for data visualization.
    4.  **Tone:** Professional, yet friendly and encouraging. Provide actionable tips and advice.
    5.  **Conclusion:** End with a summary paragraph that recaps the key takeaways.
    ---
    ### YOUR TASK ###
    Generate ONLY the Markdown body content based on the guidelines above. Do not include the title or any frontmatter.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.replace("```markdown", "").replace("```", "").strip()
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
        all_topics = list(reader)

    # [수정] 처리된 목록을 불러오고, 처리할 대상만 필터링
    processed_slugs = load_history()
    topics_to_process = [row for row in all_topics if row['slug'] not in processed_slugs]
    
    print(f"🚀 Total topics: {len(all_topics)} | Already processed: {len(processed_slugs)} | Pending: {len(topics_to_process)}")
    
    # [수정] 기존 파일 삭제 로직 제거
    # print("🔥 Deleting existing guide files to regenerate...")
    # ... (삭제 코드 제거됨) ...

    count = 0
    for row in topics_to_process:
        if LIMIT > 0 and count >= LIMIT:
            print(f"🛑 Limit reached ({LIMIT}). Stopping generation.")
            break

        slug = row['slug']
        filename = f"guide_{slug}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        content_body = generate_content(row)
        
        if content_body:
            thumbnail_url = get_thumbnail(row['category'])
            frontmatter_data = {
                "layout": "guide", "id": slug, "title": row['title'],
                "category": row['category'], "tags": [row['category']],
                "description": row['description'], "thumbnail": thumbnail_url,
                "date": time.strftime("%Y-%m-%d")
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(json.dumps(frontmatter_data, ensure_ascii=False, indent=2))
                f.write("\n---\n\n")
                f.write(content_body)
            
            # [추가] 성공 시 기록
            append_history(slug)

            print(f"✅ Saved: {filename}")
            logging.info(f"Generated: {filename}")
            count += 1
            time.sleep(3)

    print(f"✨ Job Finished. Newly generated: {count} guide(s).")

if __name__ == "__main__":
    main()