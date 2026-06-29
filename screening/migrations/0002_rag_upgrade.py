"""
Migration 0002 — SmartHire AI 2.0 RAG upgrade.

Adds:
  - Application.missing_skills (JSONField)
  - ResumeChunk model
  - AIExplanation model
  - InterviewQuestion model
  - ChatMessage model
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('screening', '0001_initial'),
    ]

    operations = [

        # ── 1. Add missing_skills to Application ─────────────────────────────
        migrations.AddField(
            model_name='application',
            name='missing_skills',
            field=models.JSONField(default=list),
        ),

        # ── 2. ResumeChunk ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ResumeChunk',
            fields=[
                ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chunk_text',  models.TextField()),
                ('chunk_type',  models.CharField(
                    max_length=30, default='general',
                    choices=[
                        ('full_overview','Full Overview'), ('summary','Summary / Objective'),
                        ('education','Education'), ('experience','Experience'),
                        ('skills','Skills'), ('projects','Projects'),
                        ('certifications','Certifications'), ('languages','Languages'),
                        ('publications','Publications'), ('general','General'),
                    ]
                )),
                ('chunk_index', models.IntegerField(default=0)),
                ('created_at',  models.DateTimeField(auto_now_add=True)),
                ('resume',      models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='chunks',
                    to='screening.resume',
                )),
                ('job',         models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='resume_chunks',
                    to='screening.job',
                )),
            ],
            options={'ordering': ['chunk_index']},
        ),

        # ── 3. AIExplanation ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='AIExplanation',
            fields=[
                ('id',                         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary',                    models.TextField(blank=True)),
                ('strengths',                  models.TextField(blank=True)),
                ('weaknesses',                 models.TextField(blank=True)),
                ('missing_skills_explanation', models.TextField(blank=True)),
                ('hiring_recommendation',      models.TextField(blank=True)),
                ('raw_text',                   models.TextField(blank=True)),
                ('generated_at',               models.DateTimeField(auto_now_add=True)),
                ('application',                models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='ai_explanation',
                    to='screening.application',
                )),
            ],
        ),

        # ── 4. InterviewQuestion ──────────────────────────────────────────────
        migrations.CreateModel(
            name='InterviewQuestion',
            fields=[
                ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question',      models.TextField()),
                ('question_type', models.CharField(
                    max_length=20, default='technical',
                    choices=[
                        ('technical','Technical'), ('project','Project-Based'),
                        ('skill_gap','Skill Gap'), ('behavioral','Behavioral'), ('hr','HR'),
                    ]
                )),
                ('order',         models.IntegerField(default=0)),
                ('application',   models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='interview_questions',
                    to='screening.application',
                )),
            ],
            options={'ordering': ['order']},
        ),

        # ── 5. ChatMessage ────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id',           models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question',     models.TextField()),
                ('answer',       models.TextField()),
                ('source_chunks',models.JSONField(default=list)),
                ('created_at',   models.DateTimeField(auto_now_add=True)),
                ('application',  models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='chat_messages',
                    to='screening.application',
                )),
            ],
            options={'ordering': ['created_at']},
        ),
    ]
