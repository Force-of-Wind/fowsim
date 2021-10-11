import re

from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.urls import reverse

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card

register = template.Library()


ATTR_TO_FILENAMES = {
    CONS.ATTRIBUTE_FIRE_CODE: 'fire.png',
    CONS.ATTRIBUTE_DARKNESS_CODE: 'darkness.png',
    CONS.ATTRIBUTE_LIGHT_CODE: 'light.png',
    CONS.ATTRIBUTE_WATER_CODE: 'water.png',
    CONS.ATTRIBUTE_WIND_CODE: 'wind.png',
    CONS.ATTRIBUTE_VOID_CODE: 'void.png'
}


@register.simple_tag
def format_cost_text(text):
    for attr in ATTR_TO_FILENAMES:
        text = text.replace('{%s}' % attr, attribute_to_img_html(attr))

    return mark_safe(text)


@register.simple_tag
def attribute_to_img_html(attr):
    return mark_safe('<img class="cost-img" src="%s">' % attribute_to_img_src(attr))


@register.simple_tag
def attribute_to_img_src(attr):
    return mark_safe(static('costs/' + ATTR_TO_FILENAMES[attr]))


def make_bubble_html(text):
    content = text[1:-1]  # Strip '[]' from the ends
    return '<div class="bubble-text">%s</div>' % content


def make_bubbles(text):
    matches = re.findall('\[[^\]]*\]', text)
    for match in matches:
        if '+' not in text:  # Skip [+X/+Y]
            text = text.replace(match, make_bubble_html(match))
    return text


def add_rest_icon(text):
    rest_url = static('imgs/rest.png')
    return text.replace('{Rest}', f'<img class="ability-rest-icon" src="{rest_url}"> ')


@register.simple_tag
def format_ability_text(text):
    text = format_cost_text(text)
    text = make_bubbles(text)
    text = add_rest_icon(text)
    text = add_card_reference_links(text)
    return mark_safe(text)


@register.simple_tag
def card_id_to_url(card_id):
    return reverse('cardDatabase-view-card', kwargs={'card_id': card_id})


def add_card_reference_links(ability_text):
    # Check for names in apostrophes
    matches = re.findall(r'"[^\"\"]+"', ability_text)
    for match in matches:
        try:
            card = Card.objects.get(name=match[1:-1])  # Trim apostrophes
            card_url = card_id_to_url(card.card_id)
            ability_text = ability_text.replace(match, f'"<a href="{card_url}">{card.name}</a>"')
        except Card.DoesNotExist:
            pass
    return ability_text


@register.simple_tag
def advanced_form_is_in_data(form_values, value, default_value, success_value):
    if not form_values:
        return default_value
    elif form_values and value in form_values:
        print(value, success_value)
        return success_value
    return ''
