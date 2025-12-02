# 🏫 JP Campus - Smart Map for Japanese Language Schools in Tokyo

JP Campus is a comprehensive service that collects and analyzes information on all Japanese language schools in Tokyo. It allows users to visualize and compare schools on a map based on **location, tuition fees, nationality ratio, and academic achievements**.

## ✨ Key Features

*   **🔍 Smart Filtering:** Search schools by region, tuition fee, Korean student ratio, dormitory availability, and more.
*   **🗺️ Map Visualization:** View exact locations and surrounding environments using Google Maps integration.
*   **📊 Detailed Insights:** Provides accurate tuition details, student demographics, and career paths extracted by AI (Gemini).
*   **🤖 Automated Pipeline:** Fully automated process from web crawling to AI data processing and geocoding.

## 🛠️ Tech Stack

*   **Language:** Python 3.11
*   **Web Framework:** FastAPI
*   **AI & Data:** Google Gemini 1.5 Flash (Data Extraction), Geopy (Geocoding)
*   **Crawling:** Requests, BeautifulSoup4
*   **Frontend:** HTML5, CSS3, Google Maps JavaScript API
*   **Infrastructure:** Google Cloud Platform (Cloud Build, Cloud Run, GCS)

## 📂 Project Structure

```text
jpcampus/
├── collect_and_convert.py  # [Core] Script for Crawling + AI Extraction + Geocoding
├── main.py                 # FastAPI Web Server (Serves the map application)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build configuration
├── cloudbuild.yaml         # Google Cloud Build configuration
├── .env                    # API Keys & Environment Variables (Create manually)
├── templates/
│   ├── index.html          # Main map view
│   └── detail.html         # School detail view
└── file/                   # Data storage directory
    └── schools_complete_db.json # Final processed database
```

## 🚀 Installation & Usage

### 1. Prerequisites

*   Python 3.11 or higher
*   Google Cloud Platform Account & Project
*   **API Keys Required:**
    *   Google Gemini API Key (Get from [Google AI Studio](https://aistudio.google.com/))
    *   Google Maps JavaScript API Key (Get from [GCP Console](https://console.cloud.google.com/))

### 2. Clone & Install Dependencies

```bash
git clone https://github.com/your-username/jpcampus.git
cd jpcampus
pip install -r requirements.txt
```

### 3. Setup Environment Variables (.env)

Create a `.env` file in the root directory and add your API keys:

```ini
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
# GCS_BUCKET_NAME=your_bucket_name (Optional: for cloud storage)
```

### 4. Data Collection (Run Once)

Execute the script to crawl data, process it with AI, and generate the JSON database.

```bash
python collect_and_convert.py
```
> This will generate `file/schools_complete_db.json`.

### 5. Run the Web Server

Start the FastAPI server locally.

```bash
uvicorn main:app --reload
```

Open your browser and visit: `http://127.0.0.1:8000`

## ☁️ Deployment (Google Cloud Run)

This project is configured for Google Cloud Build. You can deploy it using the following command (requires gcloud CLI):

```bash
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_GOOGLE_MAPS_API_KEY="your_maps_api_key"
```

## 📝 License

This project is licensed under the MIT License.
