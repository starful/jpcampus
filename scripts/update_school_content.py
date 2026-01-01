import os
import json
import time
import frontmatter
import google.generativeai as genai
from dotenv import load_dotenv
import re
import logging

load_dotenv()
CONTENT_DIR = "app/content"
LOG_DIR = "logs"
LIMIT = 1

if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
logging.basicConfig(filename=os.path.join(LOG_DIR, "school_update.log"), level=logging.INFO, format='%(asctime)s - %(message)s', encoding='utf-8')

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def clean_json(text):
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end != -1: text = text[start:end]
    text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f]', '', text)
    return text

def get_ai_enhancement(school_name, current_data):
    print(f"✍️ Analyzing (Deep): {school_name}")
    
    prompt = f"""
    You are an expert consultant for international students studying in Japan.
    Analyze the Japanese language school '{school_name}' based on the provided data and write an in-depth, comprehensive guide in ENGLISH.
    The output must be in Markdown format and follow the structure below precisely.

    **Total length must be between 7000 and 8000 characters.** Be as detailed as possible in each section.

    ---

    ## 🏫 School Overview & Philosophy
    - Write 3-4 paragraphs. Start with an engaging introduction.
    - Detail the school's location (e.g., "Located in the vibrant heart of Shinjuku..."), its specific neighborhood vibe, and proximity to major stations.
    - Explain the school's founding history, educational philosophy, and what makes it unique compared to other schools.

    ## 📚 Courses, Curriculum & Teaching Style
    - **Course Breakdown Table:** Create a detailed Markdown table with columns for | Course Name | Duration | Target Level | Key Features |.
    - **Curriculum Details:** For each main course (e.g., General, EJU Prep, Business), write a detailed paragraph explaining the curriculum, class hours, and what students will learn.
    - **Teaching Methodology:** Describe the school's teaching style. Is it strict and academic? Focused on conversation? Does it use unique materials or technology?

    ## 🌍 Student Body & Campus Life
    - **Nationality Mix Analysis:** Based on the provided demographics data, write a paragraph analyzing the student environment. For example, "With a significant portion of students from Vietnam and China, the school offers an intensive, focused learning environment..."
    - **Campus Facilities:** Describe the school's facilities: classrooms, library, student lounge, computer access, etc.
    - **Extracurricular Activities:** List and describe the cultural activities, events, or clubs offered by the school (e.g., tea ceremony, calligraphy, field trips).

    ## 🎓 University & Career Pathways
    - **Admission Records:** If data is available, create a Markdown table listing major universities students have entered.
    - **University Progression Support:** Detail the support system for students aiming for higher education: EJU prep classes, interview practice, academic counseling, university fairs, etc.
    - **Career Support:** Describe the support for job-seeking students: business Japanese classes, resume writing workshops, interview training, and partnerships with companies.

    ## 🏡 Accommodation & Living Support
    - **Dormitory Information:** Describe the types of dormitories available (single/shared, school-owned/affiliated), including average monthly cost, distance from school, and facilities.
    - **Living Assistance:** Explain how the school helps students with essential life setup, such as opening a bank account, resident registration, health insurance, and part-time job searching.

    ## 💰 Tuition, Fees & Scholarships
    - **Detailed Cost Table:** Create a Markdown table for the first-year costs: | Item | Amount (JPY) |. Include Application Fee, Admission Fee, Tuition, and Other Fees.
    - **Scholarship Programs:** List and describe available scholarships, including internal (school-offered) and external (JASSO, etc.) scholarships, mentioning eligibility criteria if possible.

    ---

    [Input Data]
    {json.dumps(current_data, ensure_ascii=False)}

    [Output Format]
    Return a JSON object with "english_slug", "features", "description_ko" (containing the detailed Markdown), and "stats".
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = clean_json(response.text)
        return json.loads(cleaned_text, strict=False) 
    except Exception as e:
        print(f"❌ AI/Network Error ({school_name}): {e}")
        logging.error(f"AI/Network Error ({school_name}): {e}")
        return None

def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"❌ {CONTENT_DIR} folder not found.")
        return

    target_files = [f for f in os.listdir(CONTENT_DIR) if re.match(r'^[A-Z0-9].*\.md$', f)]
    
    print(f"📂 Pending files: {len(target_files)}. Limit: {LIMIT}")
    logging.info(f"Start processing. Pending: {len(target_files)}")

    count = 0
    for filename in target_files:
        if count >= LIMIT:
            print(f"🛑 Limit reached ({LIMIT}). Stopping.")
            break

        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            post = frontmatter.load(filepath)
            metadata = post.metadata
            school_name = metadata.get('basic_info', {}).get('name_ja', metadata.get('title'))
            
            ai_result = get_ai_enhancement(school_name, metadata)
            if not ai_result:
                time.sleep(2)
                continue

            raw_slug = ai_result.get('english_slug', str(metadata['id'])).lower()
            new_slug = f"school_{raw_slug}" if not raw_slug.startswith("school_") else raw_slug
            new_desc = ai_result.get('description_ko', post.content)
            
            metadata['id'] = new_slug
            metadata['category'] = 'school' 
            metadata['features'] = ai_result.get('features', [])
            metadata['tags'] = metadata['features']
            metadata['thumbnail'] = "/static/img/pin-school.png" 
            if not metadata.get('stats'):
                metadata['stats'] = ai_result.get('stats', {})

            new_filename = f"{new_slug}.md"
            new_filepath = os.path.join(CONTENT_DIR, new_filename)
            
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write("---\n")
                f.write(json.dumps(metadata, ensure_ascii=False, indent=2))
                f.write("\n---\n\n")
                f.write(new_desc)
            
            print(f"   ✅ Converted: {filename} -> {new_filename}")
            logging.info(f"Success: {filename} -> {new_filename}")

            if filename != new_filename:
                os.remove(filepath)
            
            count += 1
            time.sleep(5)

        except Exception as e:
            print(f"⚠️ Unexpected Error ({filename}): {e}")
            logging.error(f"Unexpected Error {filename}: {e}")

if __name__ == "__main__":
    main()