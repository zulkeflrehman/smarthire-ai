# SmartHire AI 🤖
🚀 **Live Demo:** https://smarthire-ai-81nq.onrender.com
An AI-powered resume screening system built with Django and NLP.
Ranks candidates against a job description using a two-signal ML pipeline.

---

## Tech Stack

| Layer       | Technology |
|-------------|-----------|
| Backend     | Python 3.11 · Django 4.2 |
| ML Pipeline | scikit-learn TF-IDF · spaCy NER |
| Parsing     | pdfplumber (PDF) · python-docx (DOCX) |
| Frontend    | Bootstrap 5.3 · Chart.js · Bootstrap Icons |
| Database    | SQLite (dev) · PostgreSQL (prod) |
| Deployment  | Render.com |

---

## How the Scoring Works

Each resume is scored against the job description using two signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| TF-IDF cosine similarity | 65% | Vectorises both texts with bigram TF-IDF, measures vocabulary overlap via cosine distance |
| Skill keyword overlap | 35% | Jaccard similarity between required skills and skills extracted from the resume |

**Final Score = 0.65 × TF-IDF + 0.35 × Skill Match** (scaled 0–100)

---

## Local Setup

### Prerequisites
- Python 3.10 or 3.11
- pip

### One-command setup
```bash
git clone <your-repo-url>
cd smarthire_ai
bash setup.sh
```

### Manual setup
```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Configure environment
cp .env.example .env              # then edit .env if needed

# 5. Run migrations
python manage.py migrate

# 6. Start server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Usage

1. **Create a Job** — paste job title, description, required skills
2. **Upload Resumes** — drag & drop PDF or DOCX files (up to 50 at once)
3. **Run Screening** — one click triggers the ML pipeline
4. **Review Results** — ranked table with score rings, skill badges
5. **Shortlist / Reject** — update status per candidate inline
6. **Export CSV** — download full ranked results

---

## Project Structure

```
smarthire_ai/
├── smarthire/              # Django project config
│   ├── settings.py         # environment-aware settings
│   └── urls.py
├── screening/              # Main app
│   ├── models.py           # Job · Resume · Application
│   ├── views.py            # All view logic
│   ├── forms.py            # JobForm · ResumeUploadForm
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin
│   ├── ml/
│   │   ├── parser.py       # PDF + DOCX text extraction
│   │   ├── extractor.py    # NLP metadata extraction (spaCy)
│   │   ├── scorer.py       # TF-IDF + skill Jaccard scoring
│   │   └── pipeline.py     # Orchestration layer
│   └── templates/screening/
│       ├── base.html       # Sidebar layout
│       ├── index.html      # Dashboard
│       ├── job_list.html
│       ├── job_create.html
│       ├── job_detail.html
│       ├── upload_resumes.html
│       └── results.html    # Score rings + Chart.js histogram
├── static/
│   ├── css/custom.css      # Full design system
│   └── js/main.js
├── requirements.txt
├── Procfile                # Render/Heroku deployment
├── render.yaml             # One-click Render deploy
└── setup.sh                # Automated local setup
```

---

## Deployment (Render.com — Free)

### Option A: render.yaml (recommended)
1. Push the project to GitHub
2. Go to [render.com](https://render.com) → **New → Blueprint**
3. Connect your repo — Render reads `render.yaml` automatically
4. Click **Apply** — database + web service are created and deployed

### Option B: Manual
1. Create a **PostgreSQL** database on Render → copy the connection URL
2. Create a **Web Service** → connect your repo
3. Set environment variables:
   ```
   SECRET_KEY      = <generate a random key>
   DEBUG           = False
   ALLOWED_HOSTS   = .onrender.com
   DATABASE_URL    = <your PostgreSQL URL>
   ```
4. Build command:
   ```
   pip install -r requirements.txt && python -m spacy download en_core_web_sm && python manage.py migrate && python manage.py collectstatic --noinput
   ```
5. Start command: `gunicorn smarthire.wsgi --workers 2 --timeout 120`

---

## Admin Panel

```bash
python manage.py createsuperuser
# then visit http://127.0.0.1:8000/admin
```

---

## Portfolio Notes

### What to say in interviews / viva
- **Architecture**: Django MVT with a decoupled ML pipeline (`screening/ml/`)
- **NLP**: spaCy NER for candidate name extraction; regex for email/phone/skills
- **ML**: TF-IDF with bigram n-grams; cosine similarity for JD–resume matching
- **Skill extraction**: curated 80+ skill vocabulary across 6 domains, word-boundary regex
- **Scoring**: weighted combination of vocabulary overlap (65%) and direct skill match (35%)
- **Limitation & next step**: TF-IDF ignores semantic meaning — upgrading to BERT sentence embeddings (`sentence-transformers`) would capture paraphrases (e.g. "built REST APIs" ≈ "designed web services")
- **Deployment**: Render free tier, WhiteNoise for static files, dj-database-url for PostgreSQL

### Possible extensions (Week 2)
- Add `sentence-transformers` for BERT semantic scoring (third signal)
- User authentication (Django `allauth`)
- Email shortlist notifications
- Resume preview modal (PDF.js)
- Bulk status update

---

## License
MIT — build on it, learn from it, make it your own.
