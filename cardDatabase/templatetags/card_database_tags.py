from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def format_ability_text(text):
    return mark_safe(text)
