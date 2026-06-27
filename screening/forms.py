"""
forms.py — Django forms for SmartHire AI.
"""
from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model  = Job
        fields = ['title', 'company', 'location', 'description', 'required_skills']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Senior Backend Engineer',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Acme Corp (optional)',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Islamabad / Remote',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows':  10,
                'placeholder': 'Paste the full job description here.',
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Python, Django, REST API, PostgreSQL, Docker',
            }),
        }
        labels = {
            'required_skills': 'Required Skills (comma-separated)',
        }

    def clean_required_skills(self):
        raw = self.cleaned_data.get('required_skills', '')
        skills = [s.strip().lower() for s in raw.split(',') if s.strip()]
        return ', '.join(skills)


# ── Multi-file upload (Django 4.2 compatible) ─────────────────────────────────
class MultipleFileInput(forms.FileInput):
    """FileInput that sets allow_multiple_selected = True (Django 4.2+ requirement)."""
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        defaults = {'accept': '.pdf,.docx,.doc'}
        if attrs:
            defaults.update(attrs)
        super().__init__(attrs=defaults)


class MultipleFileField(forms.FileField):
    """FileField that returns a list of files instead of a single file."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return single(data, initial)


class ResumeUploadForm(forms.Form):
    resumes = MultipleFileField(
        label='Resume files (PDF or DOCX)',
        help_text='Select one or more resumes. Max 10 MB per file, up to 50 files.',
    )
