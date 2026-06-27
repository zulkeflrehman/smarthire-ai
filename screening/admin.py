from django.contrib import admin
from .models import Job, Resume, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = ['title', 'company', 'resume_count', 'screened_count', 'created_at']
    search_fields = ['title', 'company', 'description']
    list_filter   = ['created_at']

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display  = ['candidate_name', 'candidate_email', 'job', 'education', 'experience_years', 'uploaded_at']
    search_fields = ['candidate_name', 'candidate_email']
    list_filter   = ['job', 'education']
    readonly_fields = ['extracted_text', 'skills']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ['rank', 'resume', 'job', 'final_score', 'skill_score', 'status', 'processed_at']
    list_filter   = ['status', 'job']
    list_editable = ['status']
    ordering      = ['rank']
