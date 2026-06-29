"""
generator.py — LLM-based text generation via Groq API.

Primary:  Groq (free, fast, llama-3.1-8b-instant — 30 req/min, 6000 req/day)
Fallback: Google Gemini (gemini-1.5-flash — 15 req/min free)

Set GROQ_API_KEY in .env to enable.
Set GEMINI_API_KEY in .env to enable fallback.
"""
import os
from typing import List, Dict
from django.conf import settings


# ── Client helpers ────────────────────────────────────────────────────────────

def _groq_client():
    from groq import Groq
    key = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
    if not key:
        raise ValueError("GROQ_API_KEY not configured. Add it to your .env file.")
    return Groq(api_key=key)


def _groq_chat(prompt: str, max_tokens: int = 900, temperature: float = 0.3) -> str:
    client = _groq_client()
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


def _gemini_chat(prompt: str, max_tokens: int = 900) -> str:
    import google.generativeai as genai
    key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    if not key:
        raise ValueError("GEMINI_API_KEY not configured.")
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    resp  = model.generate_content(prompt)
    return resp.text.strip()


def _llm(prompt: str, max_tokens: int = 900, temperature: float = 0.3) -> str:
    """Try Groq first, fall back to Gemini, raise clear error if both fail."""
    errors = []
    try:
        return _groq_chat(prompt, max_tokens, temperature)
    except Exception as e:
        errors.append(f"Groq: {e}")

    try:
        return _gemini_chat(prompt, max_tokens)
    except Exception as e:
        errors.append(f"Gemini: {e}")

    raise RuntimeError(
        "No LLM available. "
        "Add GROQ_API_KEY to your .env and restart the server. "
        f"Details: {' | '.join(errors)}"
    )


# ── Context builder ───────────────────────────────────────────────────────────

def _build_context(chunks: List[Dict]) -> str:
    parts = []
    for chunk in chunks:
        section = chunk.get('chunk_type', 'general').replace('_', ' ').title()
        parts.append(f"[{section}]\n{chunk['text']}")
    return '\n\n---\n\n'.join(parts)


def _section(text: str, header: str) -> str:
    """Extract a named section from structured LLM output."""
    lines    = text.split('\n')
    capture  = False
    out      = []
    stop_on  = ['SUMMARY:', 'STRENGTHS:', 'WEAKNESSES:', 'MISSING SKILLS:', 'RECOMMENDATION:']

    for line in lines:
        upper = line.strip().upper()
        if upper.startswith(header.upper()):
            capture = True
            after   = line.split(':', 1)[-1].strip()
            if after:
                out.append(after)
            continue
        if capture:
            if any(upper.startswith(s) for s in stop_on) and not upper.startswith(header.upper()):
                break
            out.append(line)

    return '\n'.join(out).strip()


# ── Generation functions ──────────────────────────────────────────────────────

def generate_explanation(
    candidate_name: str,
    job_title: str,
    resume_chunks: List[Dict],
    job_description: str,
    final_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
) -> Dict[str, str]:
    """
    Generate a structured candidate evaluation.
    Returns dict: {summary, strengths, weaknesses, missing_skills_explanation, hiring_recommendation}
    """
    context      = _build_context(resume_chunks)
    matched_str  = ', '.join(matched_skills)  if matched_skills  else 'None identified'
    missing_str  = ', '.join(missing_skills)  if missing_skills  else 'None identified'

    prompt = f"""You are a professional HR AI assistant. Evaluate the following candidate for the job role.

JOB TITLE: {job_title}
JOB DESCRIPTION (excerpt): {job_description[:700]}

CANDIDATE: {candidate_name}
COMPOSITE MATCH SCORE: {final_score:.1f} / 100
MATCHED SKILLS: {matched_str}
MISSING SKILLS: {missing_str}

RESUME CONTENT:
{context[:3500]}

Write a structured evaluation with EXACTLY these five sections (use the exact labels below):

SUMMARY:
Write 2-3 sentences describing this candidate overall, referencing their score and key background.

STRENGTHS:
List 3-4 bullet points (use •) of their strongest qualities relevant to this role.

WEAKNESSES:
List 2-3 bullet points (use •) of gaps or concerns for this role.

MISSING SKILLS:
1-2 sentences explaining the missing skills and whether they are blockers.

RECOMMENDATION:
One of: Strongly Recommend / Recommend / Consider / Not Recommended — followed by 1-2 sentences explaining why.

Base your evaluation ONLY on the resume content provided. Do not invent information."""

    raw = _llm(prompt, max_tokens=900)
    return {
        'summary':                   _section(raw, 'SUMMARY'),
        'strengths':                 _section(raw, 'STRENGTHS'),
        'weaknesses':                _section(raw, 'WEAKNESSES'),
        'missing_skills_explanation': _section(raw, 'MISSING SKILLS'),
        'hiring_recommendation':     _section(raw, 'RECOMMENDATION'),
        'raw_text':                  raw,
    }


def generate_questions(
    candidate_name: str,
    job_title: str,
    resume_chunks: List[Dict],
    job_description: str,
    matched_skills: List[str],
    missing_skills: List[str],
) -> List[Dict]:
    """
    Generate 10 interview questions.
    Returns list of {question, question_type, order}.
    """
    context     = _build_context(resume_chunks)
    matched_str = ', '.join(matched_skills[:8]) if matched_skills else 'None'
    missing_str = ', '.join(missing_skills[:5]) if missing_skills else 'None'

    prompt = f"""You are an experienced technical interviewer. Generate 10 targeted interview questions.

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description[:600]}
CANDIDATE: {candidate_name}
MATCHED SKILLS: {matched_str}
MISSING SKILLS: {missing_str}

RESUME:
{context[:2800]}

Generate exactly 10 questions. Each line must start with one of these type labels followed by a colon:

TECHNICAL: (2 questions about their technical skills)
PROJECT: (2 questions about specific projects in their resume)
SKILL_GAP: (2 questions about skills that are missing)
BEHAVIORAL: (2 situational / behavioral questions)
HR: (2 questions about career goals or availability)

Make every question specific to THIS candidate and THIS job. No generic questions."""

    raw  = _llm(prompt, max_tokens=850, temperature=0.4)
    TYPE_MAP = {
        'TECHNICAL':  'technical',
        'PROJECT':    'project',
        'SKILL_GAP':  'skill_gap',
        'BEHAVIORAL': 'behavioral',
        'HR':         'hr',
    }

    questions = []
    order = 0
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        for label, qtype in TYPE_MAP.items():
            if line.upper().startswith(label + ':'):
                text = line[len(label) + 1:].strip()
                # strip leading list numbers or dashes
                text = text.lstrip('0123456789.-) ').strip()
                if text and len(text) > 10:
                    questions.append({'question': text, 'question_type': qtype, 'order': order})
                    order += 1
                break

    return questions[:10]


def answer_question(
    question: str,
    candidate_name: str,
    job_title: str,
    resume_chunks: List[Dict],
    job_description: str,
) -> str:
    """
    Answer a recruiter's free-form question about a candidate via RAG.
    """
    context = _build_context(resume_chunks)

    prompt = f"""You are an AI assistant helping a recruiter evaluate a job candidate.
Answer ONLY based on the resume and job description provided below.
If the information is not available, say so clearly — do not guess.

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description[:500]}

CANDIDATE: {candidate_name}
RESUME CONTEXT:
{context[:3200]}

RECRUITER QUESTION: {question}

Provide a clear, factual answer in 2-4 sentences."""

    return _llm(prompt, max_tokens=350)
