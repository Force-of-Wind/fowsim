import ast
import json
import random
import re

from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static
from django.urls import reverse
from django.db.models import Sum, Q

from cardDatabase.management.commands.importjson import remove_punctuation
from fowsim import constants as CONS
from cardDatabase.models.CardType import Card
from cardDatabase.models.Spoilers import SpoilerSeason
from cardDatabase.views import searchable_set_and_name

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
    '13': '13.png',
    '14': '14.png',
    '15': '15.png',
    '16': '16.png',
    '17': '17.png',
    '18': '18.png',
    '19': '19.png',
    '20': '20.png',
    'X': 'X.png',
    'Y': 'Y.png',
    'Z': 'Z.png',
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
    return mark_safe(static('img/costs/' + WILL_TYPE_TO_FILENAMES[str(attr)]))


@register.simple_tag
def datetime_to_timestamp(datetime):
    return datetime.timestamp()


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


def replace_angled_brackets(text):
    matches = re.findall('&lt;&lt;[\w]+&gt;&gt;', text)
    for match in matches:
        text = text.replace(match, f'<b>‹‹{match[len("&lt;&lt;"):-len("&gt;&gt;")]}››</b>')

    return text


@register.simple_tag
def format_ability_text(text):
    text = escape_tags(text)  # Must be first to escape <> before mark_safe e.g. "Force Resonance <Chaos>"
    text = replace_angled_brackets(text)
    text = format_cost_text(text)
    text = make_bubbles(text)
    text = add_rest_icon(text)
    text = add_card_reference_links(text)
    text = replace_newlines(text)
    return mark_safe(text)


@register.simple_tag
def card_id_to_url(card_id):
    return reverse('cardDatabase-view-card', kwargs={'card_id': card_id})


@register.simple_tag
def referenced_card_img_html(card):
    other_sides = card.other_sides
    if other_sides:
        output = ''
        output += '<div class="multi-hovered-img">'
        output += f'<img class="hover-card-img" src="{card.card_image.url}"/>'
        for other_card in other_sides:
            output += f'<img class="hover-card-img" src="{other_card.card_image.url}"/>'
        output += '</div>'
    else:
        output = f'<img class="hover-card-img" src="{card.card_image.url}"/>'
    return mark_safe(output)


def add_card_reference_links(ability_text):
    # Check for names in apostrophes that aren't preceded by "God's Art"
    matches = re.findall(r'(?<!God\'s Art)\s"([^\"\"]+)"', ability_text)
    for match in matches:
        try:
            try:
                card = Card.objects.get(name=match)
            except Card.MultipleObjectsReturned:
                card = Card.objects.filter(name=match).first()
            card_url = card_id_to_url(card.card_id)
            ability_text = ability_text.replace(match, f'"<a class="referenced-card" href="{card_url}">{card.name}{referenced_card_img_html(card)}</a>"')
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
def pick_period_is_in_data(form_value, value):
    default_value = ''
    if value in [str(CONS.PICK_PERIOD_NINETY_DAYS)]:
        default_value = 'checked'
    if not form_value:
        return default_value
    elif value == form_value:
        return 'checked'
    return ''

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
def map_tags(card):
    output = []
    for tag in card.card.tag.all():
        output.append(tag.id)
    if len(output) > 0:
        return mark_safe(json.dumps(ast.literal_eval(str(output))))
    else:
        return ''

@register.simple_tag
def has_tags(card):
    if len(card.card.tag.all()) > 0 and card.zone.zone.name != 'Side Deck':
        return True
    else:
        return False

@register.simple_tag
def cards_to_json(cards):
    output_cards = []
    for card in cards:
        simple_card = {
            "name": card.card.name_without_punctuation,
            "zone" : card.zone.zone.name,
            "cost": card.card.cost,
            "img":  card.card.card_image.url,
            "quantity" : card.quantity
        }
        output_cards.append(simple_card)
    return dict_to_json(output_cards)


@register.simple_tag
def colours_to_imgs(colours):
    output = ''
    for colour in colours:
        output += attribute_to_img_html(colour)
    return mark_safe(output)


@register.simple_tag
def decklist_card_count(decklist):
    return decklist.cards.aggregate(Sum('quantity'))['quantity__sum'] or 0


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


@register.simple_tag
def decklist_preview_img_url(decklist):
    ruler_cards = decklist.cards.filter(zone__zone__name='Ruler')
    if ruler_cards.exists():
        return mark_safe(ruler_cards.first().card.card_image.url)
    else:
        return base_site_icon()


@register.simple_tag
def base_site_icon():
    return mark_safe(CONS.SITE_ICON_URL)


@register.simple_tag
def get_spoiler_link():
    spoiler_sets = list(SpoilerSeason.objects.filter(is_active=True).values_list('set_code', flat=True))

    if len(spoiler_sets) == 0:
        return ''

    url = reverse('cardDatabase-search') + f'?spoiler_season={(",".join(spoiler_sets))}'
    return mark_safe(f'<a href="{url}">Spoilers</a>')


@register.simple_tag
def order_card_abilities(card):
    return card.abilities.all().order_by('position')

@register.simple_tag
def aggregate_abilties_by_style_in_order(abilities):
    result = []
    temp_list = []
    last_style = None
    last_style_name = None
    current_style = None
    current_style_name = None
    for ability in abilities:
        if ability.special_style:
            current_style = ability.special_style.identifier
            current_style_name = ability.special_style.name
        else:
            current_style = 'normal'
            current_style_name = current_style

        if current_style == last_style:
            temp_list.append(ability)
            continue

        #only add if not empty
        if temp_list:
            result.append({"style": {"id": last_style, "name": last_style_name}, "abilities": temp_list})
            temp_list = []        
        
        last_style = current_style
        last_style_name = current_style_name
        temp_list.append(ability)

    result.append({"style": {"id": last_style, "name": last_style_name}, "abilities": temp_list})

    return result


@register.simple_tag
def get_edit_decklist_url(decklist_pk, user_agent):
    if user_agent.is_mobile or user_agent.is_tablet:
        return reverse('cardDatabase-edit-decklist-mobile', kwargs={'decklist_id': decklist_pk})
    else:
        return reverse('cardDatabase-edit-decklist', kwargs={'decklist_id': decklist_pk})


@register.simple_tag
def get_card_img_urls(card):
    output = [card.card_image.url]
    other_sides = card.other_sides
    if other_sides:
        for other_side in other_sides:
            output.append(other_side.card_image.url)
    return str(output).replace('\'', '"')


@register.simple_tag
def embed_text_with_card_urls(text):
    """
    Returns a list of strings that make up the text but replaces [[Card Name]] with html that represents a URL to that
    card. The sections with HTML use mark_safe, the rest do not
    """
    output = []
    #  Either "\n" or text in "[[ ]]"
    matches = re.findall('(\[\[.*?\]\])|(\\n)', text)
    for match in matches:
        match = match[0] or match[1]
        if match == '\n':
            splits = text.split(match, 1)
            output.append(splits[0])
            output.append(mark_safe('<br />'))
            text = splits[1]
        else:
            match = match[2:-2]  # Cut off "[[ ]]"
            card = Card.objects.filter(Q(name__iexact=match) | Q(name_without_punctuation__iexact=remove_punctuation(match))).first()

            # Card not found
            if not card:
                continue

            view_card_url = reverse('cardDatabase-view-card', kwargs={"card_id": card.card_id})
            # Consume the string split by split so we can mark safe only the sections with imgs to avoid html injection
            splits = text.split(match, 1)
            output.append(splits[0][:-2])
            output.append(mark_safe(f'<a class="referenced-card" href="{view_card_url}">{card.name}{referenced_card_img_html(card)}</a>'))
            text = splits[1][2:]
    else:
        output.append(text)

    return output


@register.simple_tag
def set_code_to_name(set_code):
    return searchable_set_and_name(set_code)[1]

@register.simple_tag
def trucateText(text, trucateAt = 40):
    return (text[:trucateAt] + '...') if len(text) > trucateAt else text