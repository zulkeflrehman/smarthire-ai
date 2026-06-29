"""
retriever.py — Retrieve relevant resume chunks for a given query.

Strategy:
  Primary  → Sentence-transformer semantic cosine similarity
  Fallback → TF-IDF keyword cosine similarity (works on Render free tier)

No external vector DB needed — chunks are stored in PostgreSQL,
embeddings computed on-demand from stored text.
"""
import numpy as np
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet


# ── Semantic retrieval ────────────────────────────────────────────────────────

def _semantic_retrieve(
    question: str,
    texts: List[str],
    top_k: int,
) -> np.ndarray:
    """Cosine similarity using sentence-transformers. Returns sorted indices."""
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    model = SentenceTransformer('all-MiniLM-L6-v2')
    all_embs = model.encode([question] + texts, convert_to_numpy=True, show_progress_bar=False)
    q_emb      = all_embs[0:1]          # shape (1, 384)
    chunk_embs = all_embs[1:]           # shape (n, 384)
    sims = cosine_similarity(q_emb, chunk_embs)[0]
    return sims


# ── TF-IDF fallback retrieval ─────────────────────────────────────────────────

def _tfidf_retrieve(
    question: str,
    texts: List[str],
) -> np.ndarray:
    """TF-IDF cosine similarity — always available (scikit-learn). Returns sims array."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    corpus = [question] + texts
    vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
    try:
        mat  = vec.fit_transform(corpus)
        sims = cosine_similarity(mat[0:1], mat[1:])[0]
    except Exception:
        sims = np.ones(len(texts)) / len(texts)   # equal weight fallback
    return sims


# ── Public API ────────────────────────────────────────────────────────────────

def retrieve_chunks(
    question: str,
    chunks_qs,          # Django QuerySet[ResumeChunk]
    top_k: int = 6,
    use_semantic: bool = True,
) -> List[Dict]:
    """
    Retrieve the top-k most relevant resume chunks for a query.

    Args:
        question:     recruiter's question or generated query
        chunks_qs:    QuerySet of ResumeChunk objects for one candidate
        top_k:        number of chunks to return
        use_semantic: True → sentence-transformers; False → TF-IDF

    Returns:
        List of {'text', 'chunk_type', 'score'} sorted by score desc
    """
    chunks_list = list(chunks_qs)
    if not chunks_list:
        return []

    texts = [c.chunk_text for c in chunks_list]
    top_k = min(top_k, len(texts))

    # ── Choose retrieval method ──────────────────────────────────────────────
    sims: np.ndarray
    if use_semantic:
        try:
            sims = _semantic_retrieve(question, texts, top_k)
        except (ImportError, Exception):
            sims = _tfidf_retrieve(question, texts)
    else:
        sims = _tfidf_retrieve(question, texts)

    # ── Pick top-k ───────────────────────────────────────────────────────────
    top_indices = np.argsort(sims)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            'text':       chunks_list[idx].chunk_text,
            'chunk_type': chunks_list[idx].chunk_type,
            'score':      float(round(sims[idx], 4)),
        })

    return results
