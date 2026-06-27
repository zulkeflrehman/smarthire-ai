"""
pipeline.py — Orchestrate parse → extract → score for Django views.

Public API:
  process_single_resume(file_path)                  → {text, metadata}
  rank_resumes(jd, skills, resume_data, use_semantic) → ranked score list
"""
from typing import List, Dict

from .parser    import extract_text
from .extractor import extract_all, extract_skills
from .scorer    import (
    compute_tfidf_scores,
    compute_skill_overlap,
    compute_semantic_scores,
    compute_final_score,
)


def process_single_resume(file_path: str) -> Dict:
    """
    Parse one file and extract metadata.

    Returns:
        {"text": str, "metadata": {name, email, phone, skills, education, experience_years}}

    Raises:
        ValueError on unsupported/unreadable files.
    """
    text     = extract_text(file_path)
    metadata = extract_all(text)
    return {"text": text, "metadata": metadata}


def rank_resumes(
    job_description:     str,
    job_required_skills: str,
    resume_data:         List[Dict],
    use_semantic:        bool = True,
) -> List[Dict]:
    """
    Score and rank a batch of resumes against one job description.

    Args:
        job_description:     full JD text (used for TF-IDF and BERT)
        job_required_skills: comma-separated skills from the Job model
        resume_data:         list of {"id": int, "text": str, "skills": list[str]}
        use_semantic:        True → include BERT signal  |  False → TF-IDF + Skill only

    Returns:
        List of dicts sorted by final_score descending, each with:
        {id, tfidf_score, skill_score, semantic_score, final_score, matched_skills, rank}
    """
    if not resume_data:
        return []

    jd_combined = f"{job_description} {job_required_skills}"
    jd_skills   = extract_skills(jd_combined)
    texts       = [r["text"] for r in resume_data]

    # ── Signal 1: TF-IDF ────────────────────────────────────────────────────
    tfidf_scores = compute_tfidf_scores(job_description, texts)

    # ── Signal 3: BERT Semantic (lazy – only when enabled) ──────────────────
    if use_semantic:
        semantic_scores = compute_semantic_scores(job_description, texts)
    else:
        semantic_scores = [0.0] * len(resume_data)

    results = []
    for i, resume in enumerate(resume_data):
        tfidf    = tfidf_scores[i]
        semantic = semantic_scores[i]

        # ── Signal 2: Skill overlap ──────────────────────────────────────────
        skill_val, matched = compute_skill_overlap(jd_skills, resume.get("skills", []))

        final = compute_final_score(tfidf, skill_val, semantic)

        results.append({
            "id":             resume["id"],
            "tfidf_score":    round(tfidf    * 100, 2),
            "skill_score":    round(skill_val * 100, 2),
            "semantic_score": round(float(semantic) * 100, 2),
            "final_score":    final,
            "matched_skills": matched,
        })

    results.sort(key=lambda x: x["final_score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    return results
