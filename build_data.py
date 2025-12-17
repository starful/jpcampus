import os
import json
import frontmatter
from datetime import datetime

CONTENT_DIR = 'app/content'
OUTPUT_FILE = 'app/static/json/schools_data.json'

def main():
    print("🔨 학교 데이터 빌드 시작...")
    
    schools_list = []
    
    # 출력 폴더 생성
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE))

    if not os.path.exists(CONTENT_DIR):
        print("❌ app/content 폴더가 없습니다.")
        return

    # MD 파일 순회
    for filename in os.listdir(CONTENT_DIR):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Frontmatter 파싱
                post = frontmatter.load(f)
                meta = post.metadata
                
                # 지도 및 리스트에 필요한 핵심 정보만 추출
                school_data = {
                    "id": meta.get('id'),
                    "category": meta.get('category', 'school'), # university 또는 school
                    "basic_info": {
                        "name_ja": meta.get('basic_info', {}).get('name_ja'),
                        "address": meta.get('basic_info', {}).get('address'),
                        "capacity": meta.get('basic_info', {}).get('capacity')
                    },
                    "location": meta.get('location'),
                    "features": meta.get('features', []),
                    "tuition": meta.get('tuition'), # 필터링용
                    "stats": meta.get('stats'),     # 필터링용
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
    
    print(f"🎉 빌드 완료! 총 {len(schools_list)}개 학교 데이터 생성됨.")

if __name__ == "__main__":
    main()