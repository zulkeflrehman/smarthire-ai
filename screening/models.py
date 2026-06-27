"""
Models for SmartHire AI.

Job         — a job posting with description and required skills
Resume      — an uploaded resume file with extracted text & metadata
Application — the scored match between a Resume and a Job
"""
import os
from django.db import models


# ── Helpers ───────────────────────────────────────────────────────────────────

def resume_upload_path(instance, filename):
    """Store resumes under media/resumes/job_<id>/<filename>."""
    return f'resumes/job_{instance.job.id}/{filename}'


# ── Job ───────────────────────────────────────────────────────────────────────

class Job(models.Model):
    title           = models.CharField(max_length=200)
    company         = models.CharField(max_length=200, blank=True)
    location        = models.CharField(max_length=100, blank=True)
    description     = models.TextField(help_text="Full job description used for ML scoring.")
    required_skills = models.TextField(
        blank=True,
        help_text="Comma-separated skills, e.g. Python, Django, NLP"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}" + (f" @ {self.company}" if self.company else "")

    def get_skills_list(self):
        """Return required_skills as a cleaned Python list."""
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


# ── Resume ────────────────────────────────────────────────────────────────────

class Resume(models.Model):
    job             = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='resumes')
    file            = models.FileField(upload_to=resume_upload_path)
    candidate_name  = models.CharField(max_length=200, default='Unknown')
    candidate_email = models.EmailField(blank=True)
    candidate_phone = models.CharField(max_length=30, blank=True)
    extracted_text  = models.TextField(blank=True)
    skills          = models.JSONField(default=list)     # list of strings
    education       = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    parse_error     = models.CharField(max_length=500, blank=True)  # store any parse failure
    uploaded_at     = models.DateTimeField(auto_now_add=True)

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


# ── Application ───────────────────────────────────────────────────────────────

class Application(models.Model):
    STATUS_PENDING     = 'pending'
    STATUS_SHORTLISTED = 'shortlisted'
    STATUS_REJECTED    = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING,     'Pending Review'),
        (STATUS_SHORTLISTED, 'Shortlisted'),
        (STATUS_REJECTED,    'Rejected'),
    ]

    resume         = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='application')
    job            = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    tfidf_score    = models.FloatField(default=0, help_text="TF-IDF cosine similarity × 100")
    skill_score    = models.FloatField(default=0, help_text="Jaccard skill overlap × 100")
    semantic_score = models.FloatField(default=0, help_text="BERT sentence-embedding similarity × 100")
    final_score    = models.FloatField(default=0, help_text="Weighted composite score 0–100")
    matched_skills = models.JSONField(default=list)
    rank           = models.IntegerField(default=0)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    processed_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['rank']

    def __str__(self):
        return f"[#{self.rank}] {self.resume.candidate_name} — {self.final_score:.1f}%"

    @property
    def score_tier(self):
        """Return 'high' / 'medium' / 'low' for badge colour logic."""
        if self.final_score >= 65:
            return 'high'
        elif self.final_score >= 35:
            return 'medium'
        return 'low'

    @property
    def score_css_class(self):
        return {'high': 'success', 'medium': 'warning', 'low': 'danger'}[self.score_tier]
