from django import template

register = template.Library()

@register.filter
def dash_offset(score):
    """Compute SVG stroke-dashoffset for a score ring (circumference = 100.5)."""
    circumference = 100.5
    try:
        offset = circumference - (float(score) / 100.0) * circumference
        return round(max(offset, 0), 2)
    except (ValueError, TypeError):
        return circumference
