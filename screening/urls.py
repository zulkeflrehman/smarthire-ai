from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),

    # ── Jobs ──────────────────────────────────────────────────────────────────
    path('jobs/',                          views.job_list,       name='job_list'),
    path('jobs/new/',                      views.job_create,     name='job_create'),
    path('jobs/<int:job_id>/',             views.job_detail,     name='job_detail'),
    path('jobs/<int:job_id>/delete/',      views.job_delete,     name='job_delete'),

    # ── Resume pipeline ───────────────────────────────────────────────────────
    path('jobs/<int:job_id>/upload/',      views.upload_resumes, name='upload_resumes'),
    path('jobs/<int:job_id>/screen/',      views.screen_resumes, name='screen_resumes'),
    path('jobs/<int:job_id>/results/',     views.results,        name='results'),
    path('jobs/<int:job_id>/export/',      views.export_csv,     name='export_csv'),

    # ── Existing AJAX ─────────────────────────────────────────────────────────
    path('applications/<int:app_id>/status/',  views.update_status, name='update_status'),

    # ── NEW: RAG features (v2.0) ──────────────────────────────────────────────
    path('applications/<int:app_id>/',              views.candidate_detail,      name='candidate_detail'),
    path('applications/<int:app_id>/explain/',      views.generate_explanation,  name='generate_explanation'),
    path('applications/<int:app_id>/explain/delete/', views.delete_explanation,  name='delete_explanation'),
    path('applications/<int:app_id>/questions/',    views.generate_questions,    name='generate_questions'),
    path('applications/<int:app_id>/chat/',         views.chat_api,              name='chat_api'),
]
