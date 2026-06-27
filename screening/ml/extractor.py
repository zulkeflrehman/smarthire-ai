"""
extractor.py — Extract structured metadata from raw resume text.

Extracts:
  - Candidate name     (spaCy PERSON NER)
  - Email & phone      (regex)
  - Skills             (lookup against curated vocabulary)
  - Education level    (keyword scan)
  - Experience years   (regex)
"""
import re   
from typing import Dict, List, Optional

# ── spaCy model (small, fast, works offline) ──────────────────────────────────
try:
    import spacy
except ImportError:
    spacy = None

nlp = None

if spacy is not None:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Model is not installed. We will use fallback name extraction.
        nlp = None


# ── Skill vocabulary ──────────────────────────────────────────────────────────
# Organised by domain so we can later show coverage per category
SKILLS_BY_DOMAIN = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "ruby", "go", "rust", "swift", "kotlin", "php", "r", "scala",
        "matlab", "bash", "shell", "perl",
    ],
    "Web & Frameworks": [
        "django", "flask", "fastapi", "react", "angular", "vue", "next.js",
        "node.js", "express", "html", "css", "bootstrap", "tailwind",
        "rest api", "graphql", "jquery",
    ],
    "AI / ML / NLP": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
        "pandas", "numpy", "bert", "transformers", "hugging face",
        "reinforcement learning", "neural network", "data science",
        "text classification", "named entity recognition", "sentiment analysis",
    ],
    "Databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
        "oracle", "firebase", "elasticsearch", "dynamodb",
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "jenkins", "git", "github", "gitlab", "ci/cd", "linux", "terraform",
        "ansible", "nginx",
    ],
    "Data & Analytics": [
        "data analysis", "data visualization", "tableau", "power bi",
        "excel", "apache spark", "hadoop", "kafka", "etl", "dbt",
    ],
}

# Flat list for quick membership lookup
ALL_SKILLS: List[str] = [
    skill for skills in SKILLS_BY_DOMAIN.values() for skill in skills
]

# Sort by length descending so multi-word phrases are matched before sub-words
ALL_SKILLS.sort(key=len, reverse=True)


# ── Regex patterns ────────────────────────────────────────────────────────────
_EMAIL_RE    = re.compile(r'\b[\w.%+-]+@[\w.-]+\.[a-z]{2,}\b', re.I)
_PHONE_RE    = re.compile(r'(\+?\d[\d\s\-().]{8,14}\d)')
_EXP_RE      = re.compile(
    r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp|work)',
    re.I
)


# ── Extractors ────────────────────────────────────────────────────────────────

def extract_email(text: str) -> Optional[str]:
    m = _EMAIL_RE.search(text)
    return m.group(0) if m else None


def extract_phone(text: str) -> Optional[str]:
    m = _PHONE_RE.search(text)
    return m.group(0).strip() if m else None


def extract_skills(text: str) -> List[str]:
    """Return a deduplicated list of matched skill keywords (lowercase)."""
    text_lower = text.lower()
    found = []
    for skill in ALL_SKILLS:
        # word-boundary aware match to avoid "r" matching "rest"
        pattern = r'(?<![a-z])' + re.escape(skill) + r'(?![a-z])'
        if re.search(pattern, text_lower):
            found.append(skill)
    return list(dict.fromkeys(found))   # preserve order, dedupe


def extract_education(text: str) -> str:
    """Detect highest education level mentioned."""
    t = text.lower()
    if re.search(r'\bph\.?d\b|doctorate', t):
        return "PhD"
    if re.search(r'\bm\.?sc\b|\bm\.?s\b|master|mba|m\.?eng', t):
        return "Masters"
    if re.search(r'\bb\.?sc\b|\bb\.?s\b|bachelor|b\.?tech|b\.?e\b|b\.?cs\b', t):
        return "Bachelors"
    if re.search(r'\bassociate\b|diploma\b|intermediate', t):
        return "Associate / Diploma"
    return "Not specified"


def extract_experience_years(text: str) -> int:
    """Best-effort estimate of total years of experience."""
    matches = _EXP_RE.findall(text)
    if matches:
        return max(int(m) for m in matches)
    return 0


def extract_name(text: str) -> str:
    """
    Try to extract a person's name using spaCy NER.
    Falls back to the first non-empty line if NER finds nothing.
    """
    if nlp is None:
        return _first_line_name(text)

    # Only scan the first 500 chars — names appear at the top of a resume
    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            # Sanity check: avoid capturing email fragments
            if name and '@' not in name and len(name.split()) <= 4:
                return name

    return _first_line_name(text)


def _first_line_name(text: str) -> str:
    for line in text.split('\n')[:5]:
        line = line.strip()
        if 3 < len(line) < 60 and not any(c in line for c in ['@', ':', '/', 'http']):
            return line
    return "Unknown"


# ── Full extraction pipeline ──────────────────────────────────────────────────

def extract_all(text: str) -> Dict:
    """Run every extractor and return a single metadata dict."""
    return {
        "name":             extract_name(text),
        "email":            extract_email(text) or "",
        "phone":            extract_phone(text) or "",
        "skills":           extract_skills(text),
        "education":        extract_education(text),
        "experience_years": extract_experience_years(text),
    }
