import os
import json
import glob
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- 설정 ---
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "app", "content") # 모든 파일이 이 폴더에 위치

# 동시 처리 개수 (유료 API 사용 시 10~20, 무료는 1~2 권장)
MAX_WORKERS = 10

# API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        text = text[start:end]
    return text

def translate_file(filepath):
    filename = os.path.basename(filepath)
    name_root, ext = os.path.splitext(filename)
    
    # 타겟 파일명 생성 (예: school_abc.md -> school_abc_kr.md)
    target_filename = f"{name_root}_kr{ext}"
    target_path = os.path.join(CONTENT_DIR, target_filename)
    
    # 이미 번역된 파일이 있으면 건너뛰기 (재실행 시 속도 향상)
    if os.path.exists(target_path):
        return {"status": "skipped", "file": target_filename}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # AI 요청 데이터 준비
        input_data = {
            "filename": filename,
            "frontmatter": post.metadata,
            "content_body": post.content
        }

        # 프롬프트: 파일명 접미사 방식에 맞춘 한국어 번역 요청
        prompt = f"""
        You are a professional editor for a 'Study in Japan' platform targeting Korean students.
        Translate the provided English Markdown content into **Natural, Professional Korean**.

        **Instructions:**
        1. **Tone:** Friendly yet professional (해요체, e.g., '추천합니다', '있습니다').
        2. **Frontmatter (Metadata):**
           - Translate `title`, `description` to Korean.
           - Translate `features` list to Korean.
           - Keep `basic_info.name_en`.
           - **IMPORTANT:** Add a new field `"lang": "kr"`.
           - Do NOT change `id`, `layout`, `category`, `location`, `stats`, `tuition`.
        3. **Body Content:**
           - Translate the Markdown body to Korean.
           - Use H2 (##) for sections.
           - Ensure the content flows naturally for a Korean reader.
        
        **Output Format (JSON Only):**
        {{
            "updated_frontmatter": {{ ... }},
            "updated_body": "..."
        }}

        ---
        **Input:**
        {json.dumps(input_data, ensure_ascii=False, default=str)}
        """

        response = model.generate_content(prompt)
        cleaned_json = clean_json_response(response.text)
        result = json.loads(cleaned_json)

        new_meta = result.get('updated_frontmatter')
        new_body = result.get('updated_body')

        # [안전장치] 만약 AI가 lang을 빼먹었을 경우 강제 주입
        if new_meta:
            new_meta['lang'] = 'kr'
            
            # id는 원본과 동일하게 유지하거나, 필요시 _kr을 붙일 수 있음
            # 여기서는 URL 구조상 ID는 동일하게 유지하되 파일명으로 구분하는 것을 가정함.
            # 만약 URL도 /school/abc_kr 로 분리하려면 id에도 _kr을 붙여야 함.
            # 현재는 같은 ID를 공유하되 lang으로 내용을 갈아끼우는 방식을 대비해 ID 유지.

        # 한국어 파일 저장 (예: school_abc_kr.md)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(json.dumps(new_meta, ensure_ascii=False, indent=2))
            f.write("\n---\n\n")
            f.write(new_body)
        
        return {"status": "success", "file": target_filename}

    except Exception as e:
        return {"status": "error", "file": filename, "msg": str(e)}

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ Content directory not found: {CONTENT_DIR}")
        return

    # 원본 파일 찾기 조건:
    # 1. school_ 또는 univ_ 또는 guide_ 로 시작
    # 2. _kr.md 로 끝나지 않는 파일 (즉, 영어 원본 파일만 대상)
    all_files = glob.glob(os.path.join(CONTENT_DIR, "*.md"))
    source_files = [
        f for f in all_files 
        if (os.path.basename(f).startswith(("school_", "univ_", "guide_"))) 
        and not f.endswith("_kr.md")
    ]
    
    print(f"📂 Found {len(source_files)} English source files.")
    print(f"🚀 Generating Korean versions (*_kr.md)...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {executor.submit(translate_file, fp): fp for fp in source_files}
        
        for future in tqdm(as_completed(future_to_file), total=len(source_files), desc="Processing"):
            result = future.result()
            if result['status'] == 'error':
                tqdm.write(f"❌ Error: {result['file']} - {result['msg']}")

    print("\n✅ Korean content generation completed!")

if __name__ == "__main__":
    main()