import csv
import json
import os
import time
import requests
from tqdm import tqdm
from google.generativeai.types import GenerationConfig
from common import setup_logging, setup_gemini, clean_json_response, DATA_DIR, CONTENT_DIR, LOG_DIR

setup_logging("univ_gen.log")
model = setup_gemini()

LIMIT = 5
INPUT_CSV = os.path.join(DATA_DIR, "univ_list_100.csv")
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
    params = {"address": address, "key": GOOGLE_MAPS_API_KEY, "language": "ja"}
    try:
        res = requests.get(base_url, params=params)
        data = res.json()
        if data['status'] == 'OK':
            loc = data['results'][0]['geometry']['location']
            return {"lat": loc['lat'], "lng": loc['lng']}
    except: pass
    return {"lat": 35.6812, "lng": 139.7671}

def get_university_info(name_ja, name_en):
    print(f"🏫 AI Analysis (Deep): {name_ja}")
    prompt = f"""
    You are an expert consultant for international students planning to study in Japan.
    Analyze the university "{name_ja}" ({name_en}) and write an in-depth, comprehensive guide in ENGLISH.
    The output must be in Markdown format, follow the structure below precisely, and be **between 7000 and 8000 characters**.
    (Output JSON format with 'english_slug', 'basic_info', 'stats', 'tuition', 'faculties', 'features', 'description_ko')
    """
    for i in range(3):
        try:
            res = model.generate_content(
                prompt, generation_config=GenerationConfig(response_mime_type="application/json")
            )
            return json.loads(clean_json_response(res.text))
        except Exception as e:
            print(f"   ⚠️ Retry ({i+1}/3)... {e}")
            time.sleep(5)
    return None

def save_to_md(data):
    addr = data['basic_info'].get('address')
    coords = get_google_coordinates(addr)
    raw_slug = data.get('english_slug', data['basic_info']['name_en'].replace(" ", "-").lower())
    slug = f"univ_{raw_slug}" if not raw_slug.startswith("univ_") else raw_slug
    filepath = os.path.join(OUTPUT_DIR, f"{slug}.md")

    frontmatter_data = {
        "layout": "school", "id": slug, "title": data['basic_info']['name_ja'], "category": "university",
        "tags": data.get('features', []), "thumbnail": "/static/img/pin-univ.png", "location": coords,
        "basic_info": data['basic_info'], "stats": data['stats'], "tuition": data['tuition'],
        "faculties": data.get('faculties', []), "features": data.get('features', [])
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(json.dumps(frontmatter_data, ensure_ascii=False, indent=2))
        f.write("\n---\n\n")
        f.write(data.get('description_ko', 'No content available.'))
    return f"{slug}.md"

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ {INPUT_CSV} file not found.")
        return

    processed_list = load_history()
    univ_list = []
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['name_ja'] not in processed_list:
                univ_list.append(row)
            
    print(f"🚀 Total Universities: {len(univ_list)} | Processed: {len(processed_list)} | Target: {LIMIT}")

    count = 0
    for univ in tqdm(univ_list):
        if LIMIT > 0 and count >= LIMIT: break
        data = get_university_info(univ['name_ja'], univ['name_en'])
        if data:
            filename = save_to_md(data)
            append_history(univ['name_ja'])
            print(f"   ✅ Saved: {filename}")
            count += 1
            time.sleep(3)

if __name__ == "__main__":
    main()