from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('',                               views.index,          name='index'),

    # Jobs
    path('jobs/',                          views.job_list,       name='job_list'),
    path('jobs/new/',                      views.job_create,     name='job_create'),
    path('jobs/<int:job_id>/',             views.job_detail,     name='job_detail'),
    path('jobs/<int:job_id>/delete/',      views.job_delete,     name='job_delete'),

    # Resume processing
    path('jobs/<int:job_id>/upload/',      views.upload_resumes, name='upload_resumes'),
    path('jobs/<int:job_id>/screen/',      views.screen_resumes, name='screen_resumes'),
    path('jobs/<int:job_id>/results/',     views.results,        name='results'),
    path('jobs/<int:job_id>/export/',      views.export_csv,     name='export_csv'),

    # AJAX
    path('applications/<int:app_id>/status/', views.update_status, name='update_status'),
]
