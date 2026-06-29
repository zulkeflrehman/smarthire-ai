"""
models.py — SmartHire AI 2.0 data models.

Existing models (UNCHANGED):  Job · Resume · Application
New models (ADDED):           ResumeChunk · AIExplanation · InterviewQuestion · ChatMessage

The only change to Application is adding missing_skills JSONField.
"""
import os
from django.db import models


# ── Helpers ───────────────────────────────────────────────────────────────────

def resume_upload_path(instance, filename):
    return f'resumes/job_{instance.job.id}/{filename}'


# ═══════════════════════════════════════════════════════════════════════════════
# EXISTING MODELS — zero changes except Application.missing_skills
# ═══════════════════════════════════════════════════════════════════════════════

class Job(models.Model):
    title           = models.CharField(max_length=200)
    company         = models.CharField(max_length=200, blank=True)
    location        = models.CharField(max_length=100, blank=True)
    description     = models.TextField(help_text="Full job description used for ML scoring.")
    required_skills = models.TextField(blank=True, help_text="Comma-separated skills")
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}" + (f" @ {self.company}" if self.company else "")

    def get_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]

    @property
    def resume_count(self):
        return self.resumes.count()

    @property
    def screened_count(self):
        return self.applications.count()

    @property
    def is_screened(self):
        return self.applications.exists()


class Resume(models.Model):
    job              = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resumes')
    file             = models.FileField(upload_to=resume_upload_path)
    candidate_name   = models.CharField(max_length=200, default='Unknown')
    candidate_email  = models.EmailField(blank=True)
    candidate_phone  = models.CharField(max_length=30, blank=True)
    extracted_text   = models.TextField(blank=True)
    skills           = models.JSONField(default=list)
    education        = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    parse_error      = models.CharField(max_length=500, blank=True)
    uploaded_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.candidate_name} → {self.job.title}"

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def file_ext(self):
        return os.path.splitext(self.file.name)[1].lower()

    @property
    def has_score(self):
        return hasattr(self, 'application')

    @property
    def chunk_count(self):
        return self.chunks.count()


class Application(models.Model):
    STATUS_PENDING     = 'pending'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED    = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING,     'Pending Review'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_REJECTED,    'Rejected'),
    ]

    resume          = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='application')
    job             = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    tfidf_score     = models.FloatField(default=0)
    skill_score     = models.FloatField(default=0)
    semantic_score  = models.FloatField(default=0)
    final_score     = models.FloatField(default=0)
    matched_skills  = models.JSONField(default=list)
    missing_skills  = models.JSONField(default=list)   # ← NEW field (v2.0)
    rank            = models.IntegerField(default=0)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    processed_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"[#{self.rank}] {self.resume.candidate_name} — {self.final_score:.1f}%"

    @property
    def score_tier(self):
        if self.final_score >= 65:
            return 'high'
        elif self.final_score >= 35:
            return 'medium'
        return 'low'

    @property
    def score_css_class(self):
        return {'high': 'success', 'medium': 'warning', 'low': 'danger'}[self.score_tier]

    @property
    def has_explanation(self):
        return hasattr(self, 'ai_explanation')

    @property
    def has_questions(self):
        return self.interview_questions.exists()


# ═══════════════════════════════════════════════════════════════════════════════
# NEW MODELS — SmartHire AI 2.0 RAG features
# ═══════════════════════════════════════════════════════════════════════════════

class ResumeChunk(models.Model):
    """
    A semantic section of a resume stored for RAG retrieval.
    Created when a resume is uploaded. Deleted when the Resume is deleted.
    """
    CHUNK_TYPES = [
        ('full_overview',    'Full Overview'),
        ('summary',          'Summary / Objective'),
        ('education',        'Education'),
        ('experience',       'Experience'),
        ('skills',           'Skills'),
        ('projects',         'Projects'),
        ('certifications',   'Certifications'),
        ('languages',        'Languages'),
        ('publications',     'Publications'),
        ('general',          'General'),
    ]

    resume      = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='chunks')
    job         = models.ForeignKey(Job,    on_delete=models.CASCADE, related_name='resume_chunks')
    chunk_text  = models.TextField()
    chunk_type  = models.CharField(max_length=30, choices=CHUNK_TYPES, default='general')
    chunk_index = models.IntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_index']

    def __str__(self):
        return f"Chunk {self.chunk_index} ({self.chunk_type}) — {self.resume.candidate_name}"


class AIExplanation(models.Model):
    """
    AI-generated evaluation for one Application.
    One explanation per application (OneToOne).
    """
    application              = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name='ai_explanation'
    )
    summary                  = models.TextField(blank=True)
    strengths                = models.TextField(blank=True)
    weaknesses               = models.TextField(blank=True)
    missing_skills_explanation = models.TextField(blank=True)
    hiring_recommendation    = models.TextField(blank=True)
    raw_text                 = models.TextField(blank=True)
    generated_at             = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Explanation — {self.application.resume.candidate_name}"

    @property
    def recommendation_badge(self):
        rec = self.hiring_recommendation.lower()
        if 'strongly recommend' in rec:
            return 'success'
        if 'recommend' in rec:
            return 'primary'
        if 'consider' in rec:
            return 'warning'
        return 'danger'


class InterviewQuestion(models.Model):
    """
    AI-generated interview questions for one Application.
    Many questions per application.
    """
    QUESTION_TYPES = [
        ('technical',  'Technical'),
        ('project',    'Project-Based'),
        ('skill_gap',  'Skill Gap'),
        ('behavioral', 'Behavioral'),
        ('hr',         'HR'),
    ]
    TYPE_BADGE_COLOURS = {
        'technical':  'primary',
        'project':    'info',
        'skill_gap':  'warning',
        'behavioral': 'secondary',
        'hr':         'success',
    }

    application   = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='interview_questions'
    )
    question      = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='technical')
    order         = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order} ({self.question_type}) — {self.application.resume.candidate_name}"

    @property
    def badge_colour(self):
        return self.TYPE_BADGE_COLOURS.get(self.question_type, 'secondary')


class ChatMessage(models.Model):
    """
    A single exchange in the HR chatbot conversation about a candidate.
    """
    application      = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='chat_messages'
    )
    question         = models.TextField()
    answer           = models.TextField()
    source_chunks    = models.JSONField(default=list)   # [{text, type, score}, …]
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Chat — {self.application.resume.candidate_name} at {self.created_at:%H:%M}"
