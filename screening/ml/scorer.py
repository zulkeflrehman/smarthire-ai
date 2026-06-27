"""
scorer.py — Three-signal scoring pipeline.

Signal 1: TF-IDF cosine similarity   (keyword & context overlap)
Signal 2: Skill Jaccard overlap       (direct keyword match)
Signal 3: BERT semantic similarity    (meaning-level match via sentence-transformers)

Weights:  TF-IDF 35%  |  Skill 20%  |  BERT 45%
"""
import re
import numpy as np
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Weights (must sum to 1.0) ─────────────────────────────────────────────────
W_TFIDF    = 0.35
W_SKILL    = 0.20
W_SEMANTIC = 0.45

# ── Lazy-loaded BERT model ────────────────────────────────────────────────────
# Model: all-MiniLM-L6-v2
#   Size:    ~80 MB (downloaded once, cached in ~/.cache/torch/sentence_transformers)
#   Speed:   ~0.5–2 s per resume on CPU (i5 8th gen)
#   Strength: captures meaning — "built REST APIs" ≈ "designed web services"
#
# Why MiniLM over larger BERT?
#   - 384-dim embeddings vs 768 in bert-base → 5× faster, 6× smaller
#   - Only 2% accuracy drop on semantic benchmarks (SBERT paper, 2020)
#   - Fits comfortably in 4 GB RAM

_embed_model = None   # populated on first use


def _get_embed_model():
    """Lazy-load the sentence-transformers model (downloads once, then cached)."""
    global _embed_model
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            )
    return _embed_model


# ── Text preprocessing ────────────────────────────────────────────────────────

def _preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ── Signal 1: TF-IDF ─────────────────────────────────────────────────────────

def compute_tfidf_scores(job_description: str, resume_texts: List[str]) -> List[float]:
    """
    Batch TF-IDF cosine similarity.
    All texts share one vocabulary → fair comparison.
    Returns scores in [0, 1].
    """
    corpus = [_preprocess(job_description)] + [_preprocess(r) for r in resume_texts]
    vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english',
                          max_features=8_000, sublinear_tf=True, min_df=1)
    mat  = vec.fit_transform(corpus)
    sims = cosine_similarity(mat[0], mat[1:])[0]
    return sims.tolist()


# ── Signal 2: Skill Jaccard ───────────────────────────────────────────────────

def compute_skill_overlap(
    jd_skills: List[str],
    resume_skills: List[str],
) -> Tuple[float, List[str]]:
    """
    Jaccard similarity of two skill sets.
    Returns (score_0_to_1, matched_skill_list).
    """
    if not jd_skills:
        return 0.0, []
    a = set(s.lower() for s in jd_skills)
    b = set(s.lower() for s in resume_skills)
    inter  = a & b
    union  = a | b
    score  = len(inter) / len(union) if union else 0.0
    return score, sorted(inter)


# ── Signal 3: BERT Semantic Similarity ───────────────────────────────────────

def compute_semantic_scores(
    job_description: str,
    resume_texts: List[str],
) -> List[float]:
    """
    Encode JD and all resumes with all-MiniLM-L6-v2, then compute
    cosine similarity between the JD embedding and each resume embedding.

    Truncate input to 512 tokens (model limit) by taking the first 1500 chars
    of each document (rough heuristic — 1 token ≈ 3 chars).

    Returns scores in [0, 1].
    """
    from sentence_transformers import util

    model = _get_embed_model()

    # Truncate to avoid exceeding the model's 512-token window
    jd_text      = job_description[:1500]
    resume_texts_trunc = [r[:1500] for r in resume_texts]

    jd_emb      = model.encode(jd_text,           convert_to_tensor=True, show_progress_bar=False)
    resume_embs = model.encode(resume_texts_trunc, convert_to_tensor=True, show_progress_bar=False)

    # cosine similarity returns shape (1, n_resumes) — flatten to list
    sims = util.cos_sim(jd_emb, resume_embs)[0]
    return sims.tolist()


# ── Composite score ───────────────────────────────────────────────────────────

def compute_final_score(
    tfidf_score:    float,   # 0–1
    skill_score:    float,   # 0–1
    semantic_score: float,   # 0–1
) -> float:
    """
    Weighted sum of all three signals, scaled to 0–100.

    Weights: BERT 45%  |  TF-IDF 35%  |  Skill 20%
    BERT gets the highest weight because it captures semantic meaning
    that pure keyword matching misses.
    """
    raw = W_TFIDF * tfidf_score + W_SKILL * skill_score + W_SEMANTIC * semantic_score
    return round(min(raw * 100, 100.0), 2)
