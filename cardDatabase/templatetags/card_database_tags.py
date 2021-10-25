import random
import re

from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.urls import reverse

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card

register = template.Library()


WILL_TYPE_TO_FILENAMES = {
    CONS.ATTRIBUTE_FIRE_CODE: 'fire.png',
    CONS.ATTRIBUTE_DARKNESS_CODE: 'darkness.png',
    CONS.ATTRIBUTE_LIGHT_CODE: 'light.png',
    CONS.ATTRIBUTE_WATER_CODE: 'water.png',
    CONS.ATTRIBUTE_WIND_CODE: 'wind.png',
    CONS.ATTRIBUTE_VOID_CODE: 'void.png',
    CONS.WILL_MOON_CODE: 'moon.png,',
    CONS.WILL_TIME_CODE: 'time.png',
    '0': '0.png',
    '1': '1.png',
    '2': '2.png',
    '3': '3.png',
    '4': '4.png',
    '5': '5.png',
    '6': '6.png',
    '7': '7.png',
    '8': '8.png',
    '9': '9.png',
    '10': '10.png',
    '11': '11.png',
    '12': '12.png',
}


@register.simple_tag
def format_cost_text(text):
    for attr in WILL_TYPE_TO_FILENAMES:
        text = text.replace('{%s}' % attr, attribute_to_img_html(attr))

    return mark_safe(text)


@register.simple_tag
def attribute_to_img_html(attr):
    return mark_safe('<img class="cost-img" src="%s">' % attribute_to_img_src(attr))


@register.simple_tag
def attribute_to_img_src(attr):
    return mark_safe(static('costs/' + WILL_TYPE_TO_FILENAMES[attr]))


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
            card_img_url = static('cards/' + card.card_image_filename)
            ability_text = ability_text.replace(match, f'"<a class="referenced-card" href="{card_url}">{card.name}<img class="hover-card-img" src="{card_img_url}"/></a>"')
        except Card.DoesNotExist:
            pass
    return ability_text


@register.simple_tag
def advanced_form_is_in_data(form_values, value, default_value, success_value):
    if not form_values:
        return default_value
    elif form_values and value in form_values:
        return success_value
    return ''


@register.simple_tag
def text_exactness_is_in_data(form_values, value):
    default_value = ''
    if value == CONS.TEXT_CONTAINS_ALL:
        default_value = 'checked'
    return advanced_form_is_in_data(form_values, value, default_value, 'checked')


@register.simple_tag
def text_search_fields_is_in_data(form_values, value):
    default_value = ''
    if value in ['name', 'races__name', 'ability_texts__text']:
        default_value = 'checked'
    return advanced_form_is_in_data(form_values, value, default_value, 'checked')


@register.simple_tag
def sort_by_is_in_data(form_values, value):
    default_value = ''
    if value in [CONS.DATABASE_SORT_BY_MOST_RECENT]:
        default_value = 'checked'
    return advanced_form_is_in_data(form_values, value, default_value, 'checked')


@register.simple_tag
def get_random_chibi(category):
    return static(f'chibis/{category}/{random.choice(CONS.CHIBI_NAMES)}.png')


@register.filter
def card_referenced_by(card):
    return Card.objects.filter(ability_texts__text__contains=f'"{card.name}"')


@register.simple_tag
def format_id_text(text):
    return text.replace(CONS.DOUBLE_SIDED_CARD_CHARACTER, '*')