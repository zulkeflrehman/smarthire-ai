"""
pipeline.py — Public API for the RAG module.

Three entry points called by Django views:
  chunk_and_store_resume()     → called after resume upload
  run_explanation_pipeline()   → called when HR clicks "Generate Explanation"
  run_questions_pipeline()     → called when HR clicks "Generate Questions"
  run_chat_pipeline()          → called on every chatbot message
"""
from typing import List, Dict
from django.conf import settings

from .chunker   import chunk_resume_text
from .retriever import retrieve_chunks
from .generator import generate_explanation, generate_questions, answer_question


def _use_semantic() -> bool:
    return getattr(settings, 'USE_SEMANTIC_SCORING', True)


# ── 1. Chunk and store resume ─────────────────────────────────────────────────

def chunk_and_store_resume(resume, job) -> int:
    """
    Chunk a resume's extracted text and save chunks to PostgreSQL.
    Called once per resume upload. Returns number of chunks saved.

    Args:
        resume: Resume model instance (must have extracted_text)
        job:    Job model instance

    Returns:
        int: number of chunks created
    """
    from screening.models import ResumeChunk

    if not resume.extracted_text or len(resume.extracted_text.strip()) < 50:
        return 0

    # Remove old chunks for this resume (e.g. if re-uploaded)
    ResumeChunk.objects.filter(resume=resume, job=job).delete()

    chunks = chunk_resume_text(resume.extracted_text, resume.candidate_name)

    objs = [
        ResumeChunk(
            resume      = resume,
            job         = job,
            chunk_text  = c['chunk_text'],
            chunk_type  = c['chunk_type'],
            chunk_index = c['chunk_index'],
        )
        for c in chunks
        if c.get('chunk_text', '').strip()
    ]
    ResumeChunk.objects.bulk_create(objs)
    return len(objs)


# ── 2. Candidate explanation ──────────────────────────────────────────────────

def run_explanation_pipeline(application) -> Dict:
    """
    Generate and return an AI explanation for a screened candidate.
    The caller (view) is responsible for saving to AIExplanation model.

    Args:
        application: Application model instance

    Returns:
        dict with keys: summary, strengths, weaknesses,
                        missing_skills_explanation, hiring_recommendation
    """
    from screening.models import ResumeChunk

    resume = application.resume
    job    = application.job

    missing_skills  = application.missing_skills or []
    matched_skills  = application.matched_skills or []

    query  = f"Why is {resume.candidate_name} suitable for {job.title}?"
    chunks_qs = ResumeChunk.objects.filter(resume=resume, job=job)
    retrieved = retrieve_chunks(query, chunks_qs, top_k=6, use_semantic=_use_semantic())

    return generate_explanation(
        candidate_name = resume.candidate_name,
        job_title      = job.title,
        resume_chunks  = retrieved,
        job_description= job.description,
        final_score    = application.final_score,
        matched_skills = matched_skills,
        missing_skills = missing_skills,
    )


# ── 3. Interview questions ────────────────────────────────────────────────────

def run_questions_pipeline(application) -> List[Dict]:
    """
    Generate interview questions for a candidate.
    The caller is responsible for saving to InterviewQuestion model.

    Returns:
        list of {question, question_type, order}
    """
    from screening.models import ResumeChunk

    resume = application.resume
    job    = application.job

    missing_skills = application.missing_skills or []
    matched_skills = application.matched_skills or []

    query     = f"Skills, projects, and experience of {resume.candidate_name}"
    chunks_qs = ResumeChunk.objects.filter(resume=resume, job=job)
    retrieved = retrieve_chunks(query, chunks_qs, top_k=8, use_semantic=_use_semantic())

    return generate_questions(
        candidate_name = resume.candidate_name,
        job_title      = job.title,
        resume_chunks  = retrieved,
        job_description= job.description,
        matched_skills = matched_skills,
        missing_skills = missing_skills,
    )


# ── 4. Chatbot (ask anything about a candidate) ───────────────────────────────

def run_chat_pipeline(question: str, application) -> Dict:
    """
    Answer a free-form recruiter question about a candidate.

    Args:
        question:    recruiter's question string
        application: Application model instance

    Returns:
        {'answer': str, 'source_chunks': list of {'text', 'type', 'score'}}
    """
    from screening.models import ResumeChunk

    resume    = application.resume
    job       = application.job
    chunks_qs = ResumeChunk.objects.filter(resume=resume, job=job)
    retrieved = retrieve_chunks(question, chunks_qs, top_k=5, use_semantic=_use_semantic())

    answer = answer_question(
        question        = question,
        candidate_name  = resume.candidate_name,
        job_title       = job.title,
        resume_chunks   = retrieved,
        job_description = job.description,
    )

    return {
        'answer':       answer,
        'source_chunks': [
            {'text': c['text'][:220], 'type': c['chunk_type'], 'score': c['score']}
            for c in retrieved
        ],
    }
