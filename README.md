# 🏫 JP Campus - Smart Map for Japanese Language Schools in Tokyo

JP Campus is a comprehensive service that provides visualized data on Japanese language schools in Tokyo and Chiba. It helps prospective students compare schools based on **location, tuition fees, nationality ratio, and academic achievements** using an interactive map.

> **Key Update**: The project has been refactored for better scalability, separating frontend assets (JS/CSS) and backend logic, and introducing advanced map clustering.

## ✨ Key Features

- **🔍 Smart Filtering**:
  - **Tuition**: Filter by realistic ranges (¥850k, ¥900k, ¥1M).
  - **Nationality**: Find schools with specific demographics (Global, Low Korean ratio, High Western ratio, etc.).
  - **Location**: Filter by specific areas (Shinjuku, Ikebukuro, Chiba, etc.).
- **🗺️ Interactive Map**:
  - **Clustering**: efficiently displays hundreds of schools using `MarkerClusterer`.
  - **Performance**: Optimized rendering with Google Maps JavaScript API.
- **📊 Detailed Insights**: Provides AI-extracted data including tuition breakdown, student demographics, and career paths.
- **⚡ Modern Architecture**:
  - **FastAPI**: High-performance backend.
  - **Modular Design**: Separation of concerns (HTML/CSS/JS/Python).
  - **SEO Optimized**: JSON-LD structured data and dynamic meta tags.

## 🛠️ Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Frontend**: HTML5, CSS3, Vanilla JS (ES6+), Jinja2 Templates
- **Map & Data**: Google Maps JavaScript API, MarkerClusterer
- **AI & Crawling**: Google Gemini 1.5 Flash (Data Extraction), BeautifulSoup4
- **Infrastructure**: Google Cloud Platform (Cloud Run, Cloud Build, GCS)

## 📂 Project Structure

```text
jpcampus/
├── app/                        # Main Application Package
│   ├── __init__.py
│   ├── main.py                 # FastAPI Entry Point
│   ├── utils.py                # GCS/Local Data Loader
│   ├── static/                 # Static Assets
│   │   ├── css/
│   │   │   └── style.css       # Unified Stylesheet
│   │   └── js/
│   │       ├── i18n.js         # Internationalization (KO/JA/EN)
│   │       └── map.js          # Map Logic & Filters
│   └── templates/              # HTML Templates
│       ├── index.html          # Main Map View
│       └── detail.html         # School Detail View
├── scripts/                    # Data Collection Scripts
│   ├── collect.py              # Crawling + AI Extraction
│   └── fix_coords.py           # Geocoding Corrections
├── file/                       # Data Storage (JSON)
├── requirements.txt            # Python Dependencies
├── Dockerfile                  # Docker Configuration
└── cloudbuild.yaml             # CI/CD Configuration
```

## 🚀 Installation & Usage

### 1. Prerequisites

- Python 3.11+
- Google Cloud Platform Account
- **API Keys Required**:
  - `GEMINI_API_KEY`: For data extraction.
  - `GOOGLE_MAPS_API_KEY`: For map visualization and geocoding.

### 2. Clone & Install

```bash
git clone https://github.com/your-username/jpcampus.git
cd jpcampus
pip install -r requirements.txt
```

### 3. Setup Environment Variables (.env)

Create a `.env` file in the root directory:

```ini
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_MAPS_API_KEY=your_maps_api_key
# GCS_BUCKET_NAME=jpcampus (Optional: for cloud storage)
```

### 4. Data Collection (Run Once)

Collect school data and save it to `file/schools_complete_db.json`.

```bash
# Run the collection script
python scripts/collect.py
```

### 5. Run the Web Server

Start the FastAPI server locally. Note the change in command due to the new folder structure.

```bash
# Run from the root directory
uvicorn app.main:app --reload
```

Visit: `http://127.0.0.1:8000`

## ☁️ Deployment (Google Cloud Run)

This project is configured for **Google Cloud Build** and **Cloud Run**.

### Deploy Command

```bash
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
```

_Ensure your `Dockerfile` entrypoint is updated to:_ `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]`

## 📝 License

This project is licensed under the MIT License.
