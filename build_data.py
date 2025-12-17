# build_data.py

import os
import json
import frontmatter
from datetime import datetime
import re # 정규식 모듈 추가

CONTENT_DIR = 'app/content'
OUTPUT_FILE = 'app/static/json/schools_data.json'

def main():
    print("🔨 학교 데이터 빌드 시작...")
    
    schools_list = []
    
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE))

    if not os.path.exists(CONTENT_DIR):
        print("❌ app/content 폴더가 없습니다.")
        return

    # MD 파일 순회
    for filename in os.listdir(CONTENT_DIR):
        if not filename.endswith('.md'):
            continue
            
        # [수정] 필터링 조건 추가:
        # 파일명이 'univ_' 또는 'school_'로 시작하지 않는 파일(예: 5025.md, L002.md)은 제외
        if not (filename.startswith('univ_') or filename.startswith('school_')):
            # print(f"🚫 제외됨 (구형 데이터): {filename}")
            continue
            
        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                meta = post.metadata
                
                # 지도 및 리스트에 필요한 핵심 정보만 추출
                school_data = {
                    "id": meta.get('id'),
                    "category": meta.get('category', 'school'),
                    "basic_info": {
                        "name_ja": meta.get('basic_info', {}).get('name_ja'),
                        "address": meta.get('basic_info', {}).get('address'),
                        "capacity": meta.get('basic_info', {}).get('capacity')
                    },
                    "location": meta.get('location'),
                    "features": meta.get('features', []),
                    "tuition": meta.get('tuition'),
                    "stats": meta.get('stats'),
                    "link": f"/school/{meta.get('id')}"
                }
                schools_list.append(school_data)

        except Exception as e:
            print(f"⚠️ 에러 발생 ({filename}): {e}")

    # 최종 JSON 저장
    final_data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "schools": schools_list
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False)
    
    print(f"🎉 빌드 완료! 총 {len(schools_list)}개 정제된 데이터 생성됨.")

if __name__ == "__main__":
    main()