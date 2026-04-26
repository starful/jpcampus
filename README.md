# 🏫 JP Campus - Japan Study Abroad Platform

JP Campus is a FastAPI + Jinja2 platform for international students searching Japanese language schools, universities, and practical guides.

## ✨ Key Features

- Interactive map-based search with filtering and clustering.
- Markdown-driven CMS (`app/content`) for schools, universities, and guides.
- SEO-focused routing and templates (canonical, hreflang, sitemap, robots).
- English/Korean language support with `?lang=` query strategy.
- Deployment-ready Cloud Run pipeline with pre-deploy SEO guard.

## 🛠️ Tech Stack

- Backend: Python 3.11, FastAPI, Uvicorn
- Frontend: Jinja2, Vanilla JS, responsive CSS
- Content/Data: Markdown + JSON build pipeline
- Infra: Docker, Google Cloud Build, Cloud Run

## 📂 Project Structure

```text
jpcampus/
├── app/
│   ├── main.py                # Routes, SEO metadata, sitemap/robots, redirect middleware
│   ├── redirects.json         # Legacy URL -> new URL 301 mapping
│   ├── content/               # Markdown content source
│   ├── static/
│   │   ├── css/style.css      # UI + mobile responsive styles
│   │   └── json/              # Built school data
│   └── templates/             # Jinja templates
├── scripts/
│   ├── build_data.py          # Markdown -> static JSON build
│   ├── seo_guard.py           # SEO smoke checks (used in Cloud Build)
│   ├── 1.collect_universities.py
│   ├── 2.generate_ai_guides.py
│   ├── 3.create_korean_content.py
│   └── auto_generate_featured.py
├── tests/
│   └── test_routes.py         # Basic regression tests
├── Dockerfile
└── cloudbuild.yaml
```

## 🚀 Local Setup

### 1) Install

```bash
pip install -r requirements.txt
```

### 2) Configure environment variables

Create `.env`:

```ini
# Required
GOOGLE_MAPS_API_KEY=your_maps_api_key

# Optional content generation
GEMINI_API_KEY=your_gemini_api_key

# Optional SEO/ads settings
SITE_DOMAIN=https://jpcampus.net
GA_MEASUREMENT_ID=G-XXXXXXXXXX
ADSENSE_CLIENT_ID=ca-pub-xxxxxxxxxxxxxxxx
ADS_TXT_CONTENT=google.com, pub-xxxxxxxxxxxxxxxx, DIRECT, f08c47fec0942fa0
```

### 3) Build content data

```bash
python scripts/build_data.py
```

### 4) Run app

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000`.

## ✅ Quality & SEO Checks

### SEO guard (recommended before deploy)

```bash
python scripts/seo_guard.py
```

Checks include:
- core pages/status/canonical/noindex
- sample school/guide detail pages
- robots/sitemap validity
- sitemap `lastmod` and `hreflang`
- legacy redirect smoke check

### Basic regression tests

```bash
python -m unittest tests.test_routes
```

### CTR meta copy optimization (optional)

```bash
# Preview changes
python scripts/optimize_meta_copy.py --dry-run

# Apply to guide frontmatter
python scripts/optimize_meta_copy.py --apply
```

## 📈 Longtail Growth Starter (20 Pages)

Generate a starter batch of 20 longtail guides from a curated topic seed:

```bash
python scripts/generate_longtail_seed.py
```

Files:
- Topic seed CSV: `data/longtail_topics_seed_20.csv`
- KPI checklist: `docs/seo_longtail_kpi_checklist.md`

## 🔁 301 Redirect Management

Legacy URL redirects are controlled in `app/redirects.json`.

Example:

```json
{
  "/privacy": "/policy",
  "/guides": "/guide"
}
```

When a request results in 404, the middleware checks this map and issues `301` if matched.

## ☁️ Deployment (Cloud Run)

`cloudbuild.yaml` runs `scripts/seo_guard.py` first.  
If SEO checks fail, build/deploy is blocked automatically.

```bash
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_GOOGLE_MAPS_API_KEY="your_key"
```

## 📱 Mobile Support

The UI is mobile-responsive by default (`app/static/css/style.css`):
- optimized header/map heights for small screens
- stacked cards and filters on mobile
- wrapped footer/actions for narrow widths

## 📝 License

MIT License.