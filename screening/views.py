"""
views.py — All request handlers for SmartHire AI.
"""
import csv
import json

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import JobForm
from .ml.pipeline import process_single_resume, rank_resumes
from .models import Application, Job, Resume


# ── Dashboard ─────────────────────────────────────────────────────────────────

def index(request):
    recent_jobs    = Job.objects.all()[:6]
    total_jobs     = Job.objects.count()
    total_resumes  = Resume.objects.count()
    total_screened = Application.objects.count()
    shortlisted    = Application.objects.filter(status=Application.STATUS_SHORTLISTED).count()
    top_candidates = (
        Application.objects.select_related('resume', 'job')
        .order_by('-final_score')[:5]
    )
    return render(request, 'screening/index.html', {
        'recent_jobs':    recent_jobs,
        'total_jobs':     total_jobs,
        'total_resumes':  total_resumes,
        'total_screened': total_screened,
        'shortlisted':    shortlisted,
        'top_candidates': top_candidates,
        'use_semantic':   getattr(settings, 'USE_SEMANTIC_SCORING', True),
    })


# ── Jobs ──────────────────────────────────────────────────────────────────────

def job_list(request):
    return render(request, 'screening/job_list.html', {'jobs': Job.objects.all()})


def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Job "{job.title}" created. Now upload resumes.')
            return redirect('upload_resumes', job_id=job.pk)
    else:
        form = JobForm()
    return render(request, 'screening/job_create.html', {'form': form})


def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'screening/job_detail.html', {
        'job':          job,
        'applications': job.applications.select_related('resume').all(),
        'use_semantic': getattr(settings, 'USE_SEMANTIC_SCORING', True),
    })


def job_delete(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == 'POST':
        title = str(job)
        job.delete()
        messages.success(request, f'"{title}" deleted.')
        return redirect('job_list')
    return render(request, 'screening/job_confirm_delete.html', {'job': job})


# ── Resume upload ─────────────────────────────────────────────────────────────

def upload_resumes(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    if request.method == 'POST':
        files = request.FILES.getlist('resumes')
        if not files:
            messages.error(request, 'No files selected. Please choose at least one resume.')
            return redirect('upload_resumes', job_id=job_id)

        ok, errs = 0, []
        for f in files:
            try:
                resume = Resume(job=job, file=f)
                resume.save()

                result = process_single_resume(resume.file.path)
                meta   = result['metadata']

                resume.extracted_text   = result['text']
                resume.candidate_name   = meta.get('name', f.name)
                resume.candidate_email  = meta.get('email', '')
                resume.candidate_phone  = meta.get('phone', '')
                resume.skills           = meta.get('skills', [])
                resume.education        = meta.get('education', '')
                resume.experience_years = meta.get('experience_years', 0)
                resume.save()
                ok += 1

            except ValueError as exc:
                if 'resume' in dir():
                    resume.parse_error = str(exc)
                    resume.save()
                errs.append(f"{f.name}: {exc}")

        if ok:
            messages.success(request, f'{ok} resume{"s" if ok > 1 else ""} uploaded and parsed.')
        if errs:
            messages.warning(request, 'Issues: ' + ' | '.join(errs))

        return redirect('screen_resumes', job_id=job_id)

    return render(request, 'screening/upload_resumes.html', {'job': job})


# ── ML Screening ──────────────────────────────────────────────────────────────

def screen_resumes(request, job_id):
    """Run the full 3-signal ML pipeline and save Application records."""
    job     = get_object_or_404(Job, pk=job_id)
    resumes = job.resumes.filter(extracted_text__gt='')

    if not resumes.exists():
        messages.warning(request, 'No parsed resumes found. Upload resumes first.')
        return redirect('upload_resumes', job_id=job_id)

    # Read setting — default True (BERT on)
    use_semantic = getattr(settings, 'USE_SEMANTIC_SCORING', True)

    resume_data = [
        {'id': r.pk, 'text': r.extracted_text, 'skills': r.skills}
        for r in resumes
    ]

    results = rank_resumes(
        job_description     = job.description,
        job_required_skills = job.required_skills,
        resume_data         = resume_data,
        use_semantic        = use_semantic,
    )

    Application.objects.filter(job=job).delete()
    for r in results:
        resume = resumes.get(pk=r['id'])
        Application.objects.create(
            resume         = resume,
            job            = job,
            tfidf_score    = r['tfidf_score'],
            skill_score    = r['skill_score'],
            semantic_score = r['semantic_score'],
            final_score    = r['final_score'],
            matched_skills = r['matched_skills'],
            rank           = r['rank'],
        )

    mode = "BERT + TF-IDF + Skill" if use_semantic else "TF-IDF + Skill"
    messages.success(request, f'Screened {len(results)} resume(s) using {mode} scoring.')
    return redirect('results', job_id=job_id)


# ── Results ───────────────────────────────────────────────────────────────────

def results(request, job_id):
    job      = get_object_or_404(Job, pk=job_id)
    all_apps = job.applications.select_related('resume').all()

    if not all_apps.exists():
        messages.info(request, 'No results yet.')
        return redirect('job_detail', job_id=job_id)

    status_filter = request.GET.get('status', 'all')
    if status_filter in ('pending', 'shortlisted', 'rejected'):
        displayed = all_apps.filter(status=status_filter)
    else:
        displayed = all_apps

    paginator = Paginator(displayed, 15)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    scores    = [a.final_score for a in all_apps]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    top_score = round(max(scores), 1)                if scores else 0

    buckets = [0] * 10
    for s in scores:
        buckets[min(int(s // 10), 9)] += 1

    # Check if BERT was actually used (semantic_score > 0 on any record)
    used_semantic = all_apps.filter(semantic_score__gt=0).exists()

    return render(request, 'screening/results.html', {
        'job':           job,
        'page_obj':      page_obj,
        'all_apps':      all_apps,
        'status_filter': status_filter,
        'avg_score':     avg_score,
        'top_score':     top_score,
        'shortlisted':   all_apps.filter(status=Application.STATUS_SHORTLISTED).count(),
        'total_count':   all_apps.count(),
        'buckets_json':  json.dumps(buckets),
        'used_semantic': used_semantic,
    })


# ── AJAX status update ────────────────────────────────────────────────────────

@require_POST
def update_status(request, app_id):
    app = get_object_or_404(Application, pk=app_id)
    try:
        data       = json.loads(request.body)
        new_status = data.get('status', '')
        allowed    = {Application.STATUS_PENDING, Application.STATUS_SHORTLISTED,
                      Application.STATUS_REJECTED}
        if new_status not in allowed:
            return JsonResponse({'ok': False, 'error': 'Invalid status'}, status=400)
        app.status = new_status
        app.save(update_fields=['status'])
        return JsonResponse({'ok': True, 'status': new_status})
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'ok': False, 'error': 'Bad request'}, status=400)


# ── CSV export ────────────────────────────────────────────────────────────────

def export_csv(request, job_id):
    job      = get_object_or_404(Job, pk=job_id)
    all_apps = job.applications.select_related('resume').all()

    response = HttpResponse(content_type='text/csv')
    safe     = job.title.replace(' ', '_').replace('/', '-')
    response['Content-Disposition'] = f'attachment; filename="SmartHire_{safe}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Rank', 'Candidate', 'Email', 'Phone',
        'Final Score (%)', 'BERT Semantic (%)', 'TF-IDF (%)', 'Skill Match (%)',
        'Matched Skills', 'Education', 'Exp (yrs)', 'Status',
    ])
    for app in all_apps:
        r = app.resume
        writer.writerow([
            app.rank, r.candidate_name, r.candidate_email, r.candidate_phone,
            app.final_score, app.semantic_score, app.tfidf_score, app.skill_score,
            ', '.join(app.matched_skills),
            r.education, r.experience_years,
            app.get_status_display(),
        ])
    return response
