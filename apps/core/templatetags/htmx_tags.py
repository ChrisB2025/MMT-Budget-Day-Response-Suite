"""Custom template tags for HTMX"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def is_htmx(context):
    """Check if request is from HTMX"""
    request = context.get('request')
    if request:
        return request.headers.get('HX-Request', False)
    return False


@register.filter
def severity_color(severity):
    """Return color class based on severity level"""
    if severity >= 8:
        return 'text-red-600 bg-red-100'
    elif severity >= 5:
        return 'text-orange-600 bg-orange-100'
    else:
        return 'text-yellow-600 bg-yellow-100'


@register.filter
def status_color(status):
    """Return color class based on status"""
    colors = {
        'submitted': 'bg-gray-100 text-gray-800',
        'processing': 'bg-blue-100 text-blue-800',
        'reviewed': 'bg-green-100 text-green-800',
        'published': 'bg-purple-100 text-purple-800',
    }
    return colors.get(status, 'bg-gray-100 text-gray-800')
