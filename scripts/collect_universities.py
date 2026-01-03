import csv
import json
import os
import time
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
LIMIT = 5
INPUT_CSV = "scripts/file/univ_list_100.csv"
OUTPUT_DIR = "app/content"
LOG_DIR = "logs"
HISTORY_FILE = os.path.join(LOG_DIR, "univ_processed_history.txt")

if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

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

def clean_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1:
        return text[start:end]
    return text

def get_university_info(name_ja, name_en):
    print(f"🏫 AI Analysis (Deep): {name_ja}")
    
    prompt = f"""
    You are an expert consultant for international students planning to study in Japan.
    Analyze the university "{name_ja}" ({name_en}) and write an in-depth, comprehensive guide in ENGLISH.
    The output must be in Markdown format, follow the structure below precisely, and be **between 7000 and 8000 characters**.

    ---

    ## 🏫 University Overview & Reputation
    - Write 3-4 paragraphs. Start with a compelling introduction about the university's status in Japan (e.g., "As one of the 'Soukeisen' rivals...").
    - Detail its history, founding principles, and its academic and social reputation. Mention its ranking tier (e.g., Top private, National, etc.).

    ## 🎓 Faculties & Signature Programs
    - **Faculty Breakdown Table:** Create a Markdown table of its major faculties. Columns: | Faculty | Key Departments | Notes (e.g., 'English Program Available') |.
    - **Signature Programs:** Write detailed paragraphs about 2-3 of the university's most famous or prestigious programs, especially those attractive to international students. Explain what makes them stand out.

    ## 🌍 International Student Admissions & Life
    - **Admissions Process:** Explain the typical application process for international students (EJU requirements, English proficiency tests like TOEFL/IELTS, interviews).
    - **English-Taught Programs:** Specifically list and describe degree programs offered entirely in English. This is crucial information.
    - **Student Support:** Describe the international student office, academic advising, counseling services, and visa support systems.
    - **Campus Life & Diversity:** Talk about the number of international students, student clubs, and the overall campus atmosphere.

    ## 💰 Tuition, Scholarships & Cost of Living
    - **Detailed Cost Table:** Create a Markdown table for average first-year costs: | Item | Amount (JPY) |. Include Admission Fee, Yearly Tuition, and other relevant fees. Mention that science/engineering faculties are often more expensive.
    - **Scholarship Opportunities:** Detail major scholarships available for international students, including university-specific scholarships and government (MEXT) or private foundation scholarships.
    - **Cost of Living:** Briefly describe the average cost of living in the university's city (rent, food, transportation), providing a rough monthly budget estimate.

    ## 📍 Campus Location & Access
    - **Main Campus Vibe:** Describe the main campus's location and the character of the surrounding neighborhood (e.g., bustling city center, quiet suburb, student town).
    - **Access Table:** Create a Markdown table for accessing the main campus from major transport hubs. Columns: | From | Route | Time |.

    ---

    [Output Format - JSON Only]
    {{
        "english_slug": "university-name-slug",
        "basic_info": {{ "name_ja": "{name_ja}", "name_en": "{name_en}", "address": "Official Japanese Address", "website": "Official URL" }},
        "stats": {{ "international_students": 1234, "acceptance_rate": "15%" }},
        "tuition": {{ "admission_fee": 250000, "yearly_tuition": 1200000 }},
        "faculties": ["List of faculties"],
        "features": ["SGU", "EJU Required", "English Program", "Dormitory", "Scholarship"],
        "description_ko": "## 🏫 University Overview\\n\\n(Detailed ENGLISH content with Tables)..."
    }}
    """

    for i in range(3):
        try:
            res = model.generate_content(
                prompt, generation_config=GenerationConfig(response_mime_type="application/json")
            )
            return json.loads(clean_json(res.text))
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
        if LIMIT > 0 and count >= LIMIT:
            print(f"🛑 Limit reached ({LIMIT}). Stopping.")
            break
        data = get_university_info(univ['name_ja'], univ['name_en'])
        if data:
            filename = save_to_md(data)
            append_history(univ['name_ja'])
            print(f"   ✅ Saved: {filename}")
            count += 1
            time.sleep(3)
        else:
            print(f"   ❌ Failed: {univ['name_ja']}")

if __name__ == "__main__":
    main()