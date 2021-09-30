from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static


register = template.Library()


@register.simple_tag
def format_ability_text(text):
    return mark_safe(text)


ATTR_TO_FILENAMES = {
    'R': 'fire.png',
    'B': 'darkness.png',
    'W': 'light.png',
    'U': 'water.png',
    'G': 'wind.png',
}


@register.simple_tag
def format_cost_text(text):
    for attr in ATTR_TO_FILENAMES:
        text = text.replace('{%s}' % attr, attribute_to_img_html(attr))

    return mark_safe(text)


def attribute_to_img_html(attr):
    return '<img class="cost-img" src="%s">' % static('costs/' + ATTR_TO_FILENAMES[attr])
