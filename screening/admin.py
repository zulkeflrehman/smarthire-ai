from django.contrib import admin
from .models import (
    Job, Resume, Application,
    ResumeChunk, AIExplanation, InterviewQuestion, ChatMessage,
)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = ['title', 'company', 'resume_count', 'screened_count', 'created_at']
    search_fields = ['title', 'company']

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display  = ['candidate_name', 'candidate_email', 'job', 'education', 'experience_years', 'chunk_count', 'uploaded_at']
    search_fields = ['candidate_name', 'candidate_email']
    readonly_fields = ['extracted_text', 'skills']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ['rank', 'resume', 'job', 'final_score', 'semantic_score', 'status', 'has_explanation', 'has_questions']
    list_filter   = ['status', 'job']
    list_editable = ['status']
    ordering      = ['rank']

@admin.register(ResumeChunk)
class ResumeChunkAdmin(admin.ModelAdmin):
    list_display  = ['resume', 'chunk_type', 'chunk_index', 'created_at']
    list_filter   = ['chunk_type', 'job']
    search_fields = ['resume__candidate_name', 'chunk_text']
    readonly_fields = ['chunk_text']

@admin.register(AIExplanation)
class AIExplanationAdmin(admin.ModelAdmin):
    list_display  = ['application', 'generated_at']
    readonly_fields = ['summary', 'strengths', 'weaknesses', 'missing_skills_explanation', 'hiring_recommendation', 'raw_text']

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display  = ['order', 'question_type', 'application', 'question']
    list_filter   = ['question_type']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display  = ['application', 'question', 'created_at']
    readonly_fields = ['question', 'answer', 'source_chunks']
