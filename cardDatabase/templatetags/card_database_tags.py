import re

from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static

from fowsim import constants as CONS

register = template.Library()


ATTR_TO_FILENAMES = {
    CONS.ATTRIBUTE_FIRE_CODE: 'fire.png',
    CONS.ATTRIBUTE_DARKNESS_CODE: 'darkness.png',
    CONS.ATTRIBUTE_LIGHT_CODE: 'light.png',
    CONS.ATTRIBUTE_WATER_CODE: 'water.png',
    CONS.ATTRIBUTE_WIND_CODE: 'wind.png',
}


@register.simple_tag
def format_cost_text(text):
    for attr in ATTR_TO_FILENAMES:
        text = text.replace('{%s}' % attr, attribute_to_img_html(attr))

    return mark_safe(text)


def attribute_to_img_html(attr):
    return '<img class="cost-img" src="%s">' % static('costs/' + ATTR_TO_FILENAMES[attr])


def make_bubble_html(text):
    content = text[1:-1]  # Strip '[]' from the ends
    return '<div class="bubble-text">%s</div>' % content


def make_bubbles(text):
    matches = re.findall('\[[^\]]*\]', text)
    for match in matches:
        if '+' not in text:  # Skip [+X/+Y]
            text = text.replace(match, make_bubble_html(match))
    return text


@register.simple_tag
def format_ability_text(text):
    text = format_cost_text(text)
    text = make_bubbles(text)
    return mark_safe(text)
