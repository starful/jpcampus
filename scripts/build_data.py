# scripts/build_data.py

import os
import json
import sys
import frontmatter
from datetime import datetime
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from md_dates import ensure_post_date, save_post  # noqa: E402

CONTENT_DIR = os.path.join(BASE_DIR, 'app', 'content')
OUTPUT_DIR = os.path.join(BASE_DIR, 'app', 'static', 'json')

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

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # 영어 데이터 빌드 (기본)
    build_json('en', 'schools_data.json')
    
    # 한국어 데이터 빌드
    build_json('kr', 'schools_data_kr.json')

if __name__ == "__main__":
    main()