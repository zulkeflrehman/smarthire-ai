from django import template

register = template.Library()

@register.filter
def dash_offset(score):
    """SVG stroke-dashoffset for small ring (circumference = 100.5)."""
    try:
        return round(max(100.5 - (float(score) / 100.0) * 100.5, 0), 2)
    except (ValueError, TypeError):
        return 100.5

@register.filter
def dash_offset_lg(score):
    """SVG stroke-dashoffset for large ring (circumference = 201)."""
    try:
        return round(max(201 - (float(score) / 100.0) * 201, 0), 2)
    except (ValueError, TypeError):
        return 201

@register.filter
def split(value, delimiter='|'):
    """Split a string. Usage: {{ 'a|b|c'|split:'|' }}"""
    return str(value).split(delimiter)
