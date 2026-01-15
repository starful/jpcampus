import os
import json
import glob
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- 설정 ---
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "app", "content")

# [설정] 동시에 처리할 파일 개수 (유료 API라면 10~20도 충분히 가능)
MAX_WORKERS = 10 

# API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- 유틸리티 함수 ---
def clean_json_response(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        text = text[start:end]
    return text

def translate_file(filepath):
    """개별 파일을 처리하는 작업 함수"""
    filename = os.path.basename(filepath)
    
    try:
        # 파일 읽기
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # 1. 이미 번역된 파일 스킵 (속도 최적화)
        if post.metadata.get('translated') is True:
            return {"status": "skipped", "file": filename}

        # 2. AI 요청 데이터 준비
        input_data = {
            "frontmatter": post.metadata,
            "content_body": post.content
        }

        # 3. 프롬프트 작성
        prompt = f"""
        You are a professional editor for a Study in Japan platform.
        Convert the provided Markdown content entirely into **Natural English**.

        **Tasks:**
        1. Translate/Polish `title`, `description`, `features` in Frontmatter.
        2. Translate `basic_info.name_en` if missing or Japanese.
        3. Translate the Body Content to English.
        4. Structure body with H2 (##) and bullet points.
        5. **IMPORTANT:** Add a field `"translated": true` to the frontmatter output.

        **Output Format (JSON Only):**
        {{
            "updated_frontmatter": {{ ... }},
            "updated_body": "..."
        }}

        ---
        **Input:**
        {json.dumps(input_data, ensure_ascii=False, default=str)}
        """

        # 4. API 호출 (유료 버전이므로 대기 시간 없음)
        response = model.generate_content(prompt)
        cleaned_json = clean_json_response(response.text)
        result = json.loads(cleaned_json)

        new_meta = result.get('updated_frontmatter')
        new_body = result.get('updated_body')

        if new_meta:
            new_meta['translated'] = True

        # 5. 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(json.dumps(new_meta, ensure_ascii=False, indent=2))
            f.write("\n---\n\n")
            f.write(new_body)
        
        return {"status": "success", "file": filename}

    except Exception as e:
        return {"status": "error", "file": filename, "msg": str(e)}

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ Content directory not found.")
        return

    # 처리 대상 파일 목록 확보
    files = glob.glob(os.path.join(CONTENT_DIR, "school_*.md")) + \
            glob.glob(os.path.join(CONTENT_DIR, "univ_*.md"))
    
    print(f"📂 Total files found: {len(files)}")

    # 이미 번역된 파일 미리 필터링 (불필요한 스레드 생성 방지)
    files_to_process = []
    for fp in files:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                if "translated: true" not in f.read(500):
                    files_to_process.append(fp)
        except:
            files_to_process.append(fp)

    total_tasks = len(files_to_process)
    print(f"🚀 Starting parallel processing for {total_tasks} files with {MAX_WORKERS} workers...")

    if total_tasks == 0:
        print("🎉 All files are already translated!")
        return

    # [핵심] ThreadPoolExecutor를 사용한 병렬 처리
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 모든 작업을 스레드 풀에 등록
        future_to_file = {executor.submit(translate_file, fp): fp for fp in files_to_process}
        
        # 완료되는 대로 진행률 표시
        for future in tqdm(as_completed(future_to_file), total=total_tasks, desc="Translating"):
            result = future.result()
            if result['status'] == 'error':
                tqdm.write(f"❌ Error: {result['file']} - {result['msg']}")

    print("\n✅ Batch translation completed!")

if __name__ == "__main__":
    main()