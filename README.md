# 🤖 SmartHire AI

> **The smart way to screen job applicants — powered by AI.**

🚀 **Live Demo:** [smarthire-ai-81nq.onrender.com](https://smarthire-ai-81nq.onrender.com)
📂 **GitHub:** [github.com/zulkeflrehman/smarthire-ai](https://github.com/zulkeflrehman/smarthire-ai)

---

## 🧠 What is SmartHire AI?

SmartHire AI is a **free, open-source tool that automatically reads resumes and ranks job applicants** using artificial intelligence.

Instead of a recruiter spending hours reading 50 CVs one by one, SmartHire AI:
- Reads every resume for you (PDF or Word files)
- Compares each one to your job description
- Gives every applicant a score out of 100
- Ranks them from best match to worst — instantly

Think of it like a very smart assistant that never gets tired and reads every resume in seconds.

---

## 🎯 Who is it for?

| You are... | SmartHire AI helps you... |
|---|---|
| 🏢 **HR Manager / Recruiter** | Screen 50+ resumes in seconds, not hours |
| 🚀 **Startup Founder** | Hire smarter without a dedicated HR team |
| 🎓 **CS / AI Student** | See a real-world NLP + Django project in action |
| 👨‍💼 **Freelance Consultant** | Offer resume screening as a service to clients |

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 **Bulk Resume Upload** | Upload up to 50 PDF or DOCX resumes at once |
| 🤖 **3-Signal AI Scoring** | BERT Semantic + TF-IDF + Skill Matching combined |
| 📊 **Score Rings & Charts** | Visual score indicators and distribution histogram |
| 🔍 **Real-time Search & Filter** | Search by name, email, or skill — results update instantly |
| 📋 **Expandable Row Details** | Click any candidate to see full skills breakdown inline |
| 💬 **AI Chat per Candidate** | Ask the AI anything about a specific candidate |
| 📝 **Interview Questions** | Auto-generate tailored interview questions per candidate |
| ✅ **Shortlist / Reject** | Mark candidates inline — no page reload |
| 📥 **Export CSV** | Download all results as a spreadsheet |
| 🌙 **Obsidian Dark Theme** | Beautiful premium dark UI |

---

## 🔍 How the Scoring Works (Plain English)

When you upload resumes, SmartHire AI uses **three signals** to score each candidate:

### Signal 1 — BERT Semantic Matching (45%)
Reads the *meaning* of the resume, not just the words. So if the job says "built REST APIs" and the resume says "developed web services", it still recognizes they mean the same thing.

### Signal 2 — TF-IDF Keyword Matching (35%)
Looks for specific words and phrases that overlap between the resume and job description. Classic but effective.

### Signal 3 — Skill Keyword Match (20%)
Checks how many of the required skills (e.g. Python, Django, SQL) actually appear in the resume.

**Final Score = weighted combination of all 3 signals, scaled 0–100**

> On the live hosted version, BERT is disabled to stay within free server RAM limits. TF-IDF + Skills are still used (great accuracy for most jobs).

---

## 🚀 How to Use SmartHire AI (Step by Step)

### Step 1 — Create a Job
Click **"New Job"** in the sidebar. Enter:
- Job title (e.g. "Backend Developer")
- Job description (paste from LinkedIn, indeed, etc.)
- Required skills (comma-separated: `Python, Django, SQL`)

### Step 2 — Upload Resumes
Click **"Upload Resumes"** on the job page. Drag and drop up to 50 PDF or DOCX files.

### Step 3 — Run Screening
Click **"Screen Resumes"**. The AI pipeline runs in seconds and ranks all candidates.

### Step 4 — Review Results
See all candidates ranked by score. Use the **search box**, **score filter**, and **status filter** to zero in on the best matches.

### Step 5 — Expand any Candidate
Click on any row to instantly see their **matched skills**, **missing skills**, education, and experience — without leaving the page.

### Step 6 — Use the AI Chat
Open a candidate's full profile to:
- Read the AI-generated evaluation summary
- Ask the AI anything: *"Why is this candidate a good fit?"*, *"What are their weak points?"*
- Get tailored interview questions

### Step 7 — Shortlist or Reject
Use the **Status** dropdown on each row to mark candidates as Shortlisted ✓ or Rejected ✗.

### Step 8 — Export
Click **Export CSV** to download all results as a spreadsheet.

---

## 🛠️ Local Setup (Run on Your Computer)

### Requirements
- Python 3.10 or 3.11
- pip

### Quick Setup (One Command)
```bash
git clone https://github.com/zulkeflrehman/smarthire-ai.git
cd smarthire-ai
bash setup.sh
```

### Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy language model
python -m spacy download en_core_web_sm

# 5. Set up environment variables
cp .env.example .env
# Then open .env and fill in your GROQ_API_KEY

# 6. Run database migrations
python manage.py migrate

# 7. Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser — done! 🎉

### Getting a Free GROQ API Key (for AI Chat)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free
3. Click **"API Keys"** → **"Create API Key"**
4. Copy the key and paste it in your `.env` file as `GROQ_API_KEY=your_key_here`
5. Restart the server

---

## ☁️ Deploy Live on Render.com (Free)

Render.com lets you host the app for free with a database included.

### Option A — One-Click Blueprint (Recommended)
1. **Push this repo to your GitHub account**
2. Go to [render.com](https://render.com) → Sign up (free)
3. Click **New → Blueprint**
4. Connect your GitHub repo
5. Render reads `render.yaml` and sets up everything automatically
6. Click **Apply** — the database and web service are created and deployed

**After deploy:**
- Open the Render dashboard → Your web service → **Environment**
- Add `GROQ_API_KEY` = your key from [console.groq.com](https://console.groq.com)
- Click **Save** → the service restarts automatically

### Option B — Manual Setup
1. Create a **PostgreSQL** database on Render → copy the connection URL
2. Create a **Web Service** → connect your GitHub repo
3. Set these environment variables:
   ```
   SECRET_KEY      = (Render can generate this for you)
   DEBUG           = False
   ALLOWED_HOSTS   = .onrender.com
   DATABASE_URL    = (your PostgreSQL connection URL)
   GROQ_API_KEY    = (your key from console.groq.com)
   ```
4. **Build command:**
   ```
   pip install --prefer-binary -r requirements-render.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
5. **Start command:**
   ```
   gunicorn smarthire.wsgi --workers 2 --timeout 120
   ```

> ⚠️ **Note:** The free Render tier has 512MB RAM and sleeps after 15 min of inactivity. First load after sleep takes ~30 seconds. Upgrade to a paid plan for production use.

---

## 🏗️ Project Structure

```
smarthire_ai/
├── smarthire/               # Django project config
│   ├── settings.py          # Environment-aware settings (dev/prod)
│   └── urls.py              # Root URL routing
├── screening/               # Main application
│   ├── models.py            # Job · Resume · Application models
│   ├── views.py             # All page view logic
│   ├── urls.py              # App URL routing
│   ├── ml/
│   │   ├── parser.py        # PDF + DOCX text extraction
│   │   ├── extractor.py     # NLP metadata (spaCy — name, email, skills)
│   │   ├── scorer.py        # TF-IDF + Skill scoring engine
│   │   └── pipeline.py      # Orchestration: runs all signals
│   ├── rag/
│   │   ├── retriever.py     # Splits resume into chunks for AI context
│   │   └── generator.py     # Groq LLM integration (chat, questions)
│   └── templates/screening/
│       ├── base.html        # Sidebar layout shell
│       ├── index.html       # Dashboard
│       ├── results.html     # Ranked candidates + interactive filters
│       ├── candidate_detail.html  # AI profile + chat
│       └── about.html       # How to use guide
├── static/
│   ├── css/custom.css       # Full Obsidian Glass design system
│   └── js/main.js
├── requirements.txt         # Local development dependencies
├── requirements-render.txt  # Production dependencies (no spaCy/BERT)
├── render.yaml              # Render.com one-click deploy config
├── Procfile                 # Process file for deployment
├── runtime.txt              # Python version pin (3.11.7)
└── setup.sh                 # Automated local setup script
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11 · Django 4.2 |
| **AI Scoring** | sentence-transformers (BERT) · scikit-learn TF-IDF · spaCy NER |
| **LLM / Chat** | Groq API (llama-3.1-8b-instant — free, fast) |
| **Resume Parsing** | pdfplumber (PDF) · python-docx (DOCX) |
| **Frontend** | Vanilla CSS · Bootstrap 5.3 · Chart.js · Bootstrap Icons |
| **Database** | SQLite (local dev) · PostgreSQL (production) |
| **Deployment** | Render.com · WhiteNoise static files · Gunicorn WSGI |

---

## 🤔 FAQ

**Q: Is my data private?**
A: Resume text is processed on your own server. The only external call is to the Groq API for AI chat — resume text is sent to Groq's servers to generate responses. If privacy is critical, you can run the app fully locally with no Groq key (scoring still works, AI chat will be disabled).

**Q: Does it work without the GROQ API key?**
A: Yes! Resume scoring, ranking, filtering, and CSV export all work without it. The API key is only needed for AI chat, interview question generation, and candidate explanations.

**Q: How many resumes can it handle?**
A: Up to 50 resumes per upload batch. You can run multiple batches for the same job.

**Q: What file formats are supported?**
A: PDF and DOCX (Microsoft Word). Other formats are not supported yet.

**Q: Can I use it for free forever?**
A: Yes — the code is MIT licensed, completely open source. Render's free tier is sufficient for light use.

---

## 📄 License
MIT — use it, learn from it, build on it, make it your own.

---

## 👤 Author
Built by **Zulkefl Rehman** as an AI/ML final-year project at IIUI.
