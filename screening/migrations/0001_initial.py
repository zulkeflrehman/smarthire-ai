# Generated migration for SmartHire AI — includes semantic_score from the start

from django.db import migrations, models
import django.db.models.deletion
import screening.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',           models.CharField(max_length=200)),
                ('company',         models.CharField(blank=True, max_length=200)),
                ('location',        models.CharField(blank=True, max_length=100)),
                ('description',     models.TextField(help_text='Full job description used for ML scoring.')),
                ('required_skills', models.TextField(blank=True, help_text='Comma-separated skills')),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id',               models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file',             models.FileField(upload_to=screening.models.resume_upload_path)),
                ('candidate_name',   models.CharField(default='Unknown', max_length=200)),
                ('candidate_email',  models.EmailField(blank=True, max_length=254)),
                ('candidate_phone',  models.CharField(blank=True, max_length=30)),
                ('extracted_text',   models.TextField(blank=True)),
                ('skills',           models.JSONField(default=list)),
                ('education',        models.CharField(blank=True, max_length=100)),
                ('experience_years', models.IntegerField(default=0)),
                ('parse_error',      models.CharField(blank=True, max_length=500)),
                ('uploaded_at',      models.DateTimeField(auto_now_add=True)),
                ('job',              models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to='screening.job')),
            ],
            options={'ordering': ['-uploaded_at']},
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id',             models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tfidf_score',    models.FloatField(default=0, help_text='TF-IDF cosine similarity × 100')),
                ('skill_score',    models.FloatField(default=0, help_text='Jaccard skill overlap × 100')),
                ('semantic_score', models.FloatField(default=0, help_text='BERT sentence-embedding similarity × 100')),
                ('final_score',    models.FloatField(default=0, help_text='Weighted composite score 0–100')),
                ('matched_skills', models.JSONField(default=list)),
                ('rank',           models.IntegerField(default=0)),
                ('status',         models.CharField(
                    choices=[('pending', 'Pending Review'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected')],
                    default='pending', max_length=20
                )),
                ('processed_at',   models.DateTimeField(auto_now_add=True)),
                ('job',            models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='screening.job')),
                ('resume',         models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='application', to='screening.resume')),
            ],
            options={'ordering': ['rank']},
        ),
    ]
