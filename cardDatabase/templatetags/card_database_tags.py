import ast
import json
import random
import re

from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.urls import reverse
from django.db.models import Sum

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
    CONS.WILL_MOON_CODE: 'moon.png',
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
    'X': 'X.png',
}


@register.simple_tag
def format_cost_text(text):
    for attr in WILL_TYPE_TO_FILENAMES:
        text = text.replace('{%s}' % attr, attribute_to_img_html(attr))

    return mark_safe(text)


@register.simple_tag
def format_attribute_text(attr):
    return attribute_to_img_html(attr)


@register.simple_tag
def attribute_to_img_html(attr):
    return mark_safe('<img class="cost-img" src="%s">' % attribute_to_img_src(attr))


@register.simple_tag
def attribute_to_img_src(attr):
    return mark_safe(static('img/costs/' + WILL_TYPE_TO_FILENAMES[attr]))


def make_bubble_html(text):
    content = text[1:-1]  # Strip '[]' from the ends
    return '<div class="bubble-text">%s</div>' % content


def make_bubbles(text):
    matches = re.findall('\[[^\]]*\]', text)
    for match in matches:
        if '/' not in match:  # Skip any ATK/DEF
            text = text.replace(match, make_bubble_html(match))
    return text


def add_rest_icon(text):
    rest_url = static('img/rest.png')
    return text.replace('{Rest}', f'<img class="ability-rest-icon" src="{rest_url}"> ')


def escape_tags(text):
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def replace_newlines(text):
    return text.replace('\n', '<br />')


@register.simple_tag
def format_ability_text(text):
    text = escape_tags(text)  # Must be first to escape <> before mark_safe e.g. "Force Resonance <Chaos>"
    text = format_cost_text(text)
    text = make_bubbles(text)
    text = add_rest_icon(text)
    text = add_card_reference_links(text)
    text = replace_newlines(text)
    return mark_safe(text)


@register.simple_tag
def card_id_to_url(card_id):
    return reverse('cardDatabase-view-card', kwargs={'card_id': card_id})


def add_card_reference_links(ability_text):
    # Check for names in apostrophes
    matches = re.findall(r'"[^\"\"]+"', ability_text)
    for match in matches:
        try:
            try:
                card = Card.objects.get(name=match[1:-1])
            except Card.MultipleObjectsReturned:
                card = Card.objects.filter(name=match[1:-1]).first()
            card_url = card_id_to_url(card.card_id)
            ability_text = ability_text.replace(match, f'"<a class="referenced-card" href="{card_url}">{card.name}<img class="hover-card-img" src="{card.card_image.url}"/></a>"')
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
def colour_match_is_in_data(form_values, value):
    default_value = ''
    if value in [CONS.DATABASE_COLOUR_MATCH_ANY]:
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
    return static(f'img/chibis/{category}/{random.choice(CONS.CHIBI_NAMES)}.png')


@register.filter
def card_referenced_by(card):
    return Card.objects.filter(ability_texts__text__contains=f'"{card.name}"')


@register.simple_tag
def format_id_text(text):
    return text.replace(CONS.DOUBLE_SIDED_CARD_CHARACTER, '*')


@register.simple_tag
def dict_to_json(dict_obj):
    return mark_safe(json.dumps(ast.literal_eval(str(dict_obj))))


@register.simple_tag
def colours_to_imgs(colours):
    output = ''
    for colour in colours:
        output += attribute_to_img_html(colour)
    return mark_safe(output)


@register.simple_tag
def decklist_card_count(decklist):
    return decklist.cards.aggregate(Sum('quantity'))['quantity__sum']


@register.simple_tag
def untap_list(cards):
    starting_area = []
    main = []
    sideboard = []
    stone_deck = []
    face_down = []
    for card in cards:
        if card.zone.zone.name == 'Main Deck':
            main.append(card)
        elif card.zone.zone.name == 'Side Deck':
            sideboard.append(card)
        elif card.zone.zone.name == 'Magic Stone Deck':
            stone_deck.append(card)
        elif card.zone.zone.name == 'Ruler':
            starting_area.append(card)
        elif ('stranger' in card.zone.zone.name.lower() or
              'rune' in card.zone.zone.name.lower() or
              'extra' in card.zone.zone.name.lower()):
            face_down.append(card)

    output = ''
    if len(main) > 0:
        output += '//deck-1\n'
        for card in main:
            output += f'{str(card.quantity)} {card.card.name}\n'
        output += '\n'

    if len(starting_area) > 0:
        output += '//play-1\n'
        for card in starting_area:
            output += f'{str(card.quantity)} {card.card.name}\n'
        output += '\n'

    if len(sideboard) > 0:
        output += '//sideboard-1\n'
        for card in sideboard:
            output += f'{str(card.quantity)} {card.card.name}\n'
        output += '\n'

    if len(stone_deck) > 0:
        output += '//deck-2\n'
        for card in stone_deck:
            output += f'{str(card.quantity)} {card.card.name}\n'
        output += '\n'

    if len(face_down) > 0:
        output += '//pile-facedown\n'
        for card in face_down:
            output += f'{str(card.quantity)} {card.card.name}\n'
        output += '\n'
    return output
