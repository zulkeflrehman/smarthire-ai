"""
chunker.py — Split resume text into semantic sections for RAG retrieval.

Strategy:
  1. Detect section headers (EDUCATION, EXPERIENCE, SKILLS, PROJECTS…)
  2. Split text along detected headers
  3. Fallback to sliding-window if headers are absent
  4. Always add a full-text overview chunk
"""
import re
from typing import List, Dict

# Regex patterns for common resume section headers
SECTION_PATTERNS = {
    'summary':          r'(?i)^(summary|objective|profile|about me|overview|introduction)',
    'education':        r'(?i)^(education|academic|qualification|degree|university|college|studies)',
    'experience':       r'(?i)^(experience|work experience|employment|career|internship|positions held)',
    'skills':           r'(?i)^(skills|technical skills|technologies|tools|competencies|expertise|key skills)',
    'projects':         r'(?i)^(projects?|portfolio|work samples?|case studies?|personal projects?)',
    'certifications':   r'(?i)^(certifications?|certificates?|awards?|achievements?|accomplishments?)',
    'languages':        r'(?i)^(languages?|spoken|written|linguistic)',
    'publications':     r'(?i)^(publications?|research|papers?|thesis)',
}


def _is_section_header(line: str) -> str | None:
    """
    Detect if a line is a section header.
    Returns section name or None.
    """
    line = line.strip()
    if not line or len(line) > 60:
        return None

    # Must look like a heading: all-caps, title-case, or ends with colon
    looks_like_header = (
        line.isupper() or
        (line.istitle() and len(line.split()) <= 4) or
        line.endswith(':') or
        line.endswith('—') or
        re.match(r'^[A-Z][A-Z\s&/]+$', line)
    )
    if not looks_like_header:
        return None

    for section_name, pattern in SECTION_PATTERNS.items():
        if re.search(pattern, line):
            return section_name

    return None


def chunk_resume_text(text: str, candidate_name: str = '') -> List[Dict]:
    """
    Split resume text into semantic chunks.

    Returns:
        List of dicts: {chunk_text, chunk_type, chunk_index}
    """
    lines = [l.strip() for l in text.split('\n')]
    chunks: List[Dict] = []
    current_section = 'general'
    current_lines: List[str] = []
    chunk_index = 0

    for line in lines:
        if not line:
            continue

        detected = _is_section_header(line)
        if detected and current_lines:
            # Flush current buffer as a chunk
            chunk_text = '\n'.join(current_lines).strip()
            if len(chunk_text) > 40:
                chunks.append({
                    'chunk_text': chunk_text,
                    'chunk_type': current_section,
                    'chunk_index': chunk_index,
                })
                chunk_index += 1
            current_lines = [line]
            current_section = detected
        else:
            current_lines.append(line)

    # Flush remaining lines
    if current_lines:
        chunk_text = '\n'.join(current_lines).strip()
        if len(chunk_text) > 40:
            chunks.append({
                'chunk_text': chunk_text,
                'chunk_type': current_section,
                'chunk_index': chunk_index,
            })

    # If no meaningful sections found, fall back to sliding window
    if len(chunks) <= 1:
        chunks = _sliding_window_chunks(text)

    # Always prepend a full-overview chunk (first 2000 chars)
    overview_text = text[:2000].strip()
    if overview_text and len(overview_text) > 100:
        chunks.insert(0, {
            'chunk_text': overview_text,
            'chunk_type': 'full_overview',
            'chunk_index': 0,
        })
        # Re-index
        for i, c in enumerate(chunks):
            c['chunk_index'] = i

    return chunks


def _sliding_window_chunks(
    text: str,
    window_words: int = 150,
    overlap_words: int = 30,
) -> List[Dict]:
    """
    Fallback chunking: overlapping windows of words.
    """
    words = text.split()
    chunks = []
    i = 0
    idx = 0

    while i < len(words):
        chunk_words = words[i: i + window_words]
        chunk_text = ' '.join(chunk_words)
        if len(chunk_text) > 50:
            chunks.append({
                'chunk_text': chunk_text,
                'chunk_type': 'general',
                'chunk_index': idx,
            })
        i += window_words - overlap_words
        idx += 1

    return chunks
