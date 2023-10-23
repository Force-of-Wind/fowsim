from django.utils.safestring import mark_safe
from django.templatetags.static import static

from fowsim.utils import listToChoices

CARD_POSITION_TOP = 'Top'
CARD_POSITION_BOTTOM = 'Bottom'
CARD_POSITION_X_FROM_TOP = "X From Top"
CARD_POSITION_X_FROM_BOTTOM = "X From Bottom"
CARD_POSITION_PLAYERS_CHOICE = "Player's Choice"
CARD_POSITION_UNORDERED_AREA = "Unordered"

MOVE_CARD_POSITION_CHOICES_VALUES = [
    CARD_POSITION_TOP,
    CARD_POSITION_BOTTOM,
    CARD_POSITION_X_FROM_TOP,
    CARD_POSITION_X_FROM_BOTTOM,
    CARD_POSITION_PLAYERS_CHOICE,
    CARD_POSITION_UNORDERED_AREA,
]


EFFECT_AREA_EFFECT_CONTROLLER = "Effect's Controller"
EFFECT_AREA_EFFECT_CONTROLLER_OPPONENT = "Effect's Controller's Opponent"
EFFECT_AREA_CHOICES_VALUES = [
    EFFECT_AREA_EFFECT_CONTROLLER,
    EFFECT_AREA_EFFECT_CONTROLLER_OPPONENT,
]

RARITY_COMMON = 'Common'
RARITY_UNCOMMON = 'Uncommon'
RARITY_RARE = 'Rare'
RARITY_SUPER_RARE = 'Super Rare'
RARITY_EXTENSION_RARE = 'Extension Rare'
RARITY_TOKEN = 'Token'
RARITY_MARVEL_RARE = 'Marvel Rare'
RARITY_RULER = 'Ruler'
RARITY_J_RULER = 'J-Ruler'
RARITY_COLOSSAL_J_RULER = 'Colossal J-Ruler'
RARITY_NORMAL = 'Normal'
RARITY_SECRET_RARE = 'Secret Rare'
RARITY_ASCENDED_RULER = 'Ascended Ruler'
RARITY_ASCENDED_J_RULER = 'Ascended J-ruler'

RARITY_COMMON_VALUE = 'C'
RARITY_UNCOMMON_VALUE = 'U'
RARITY_RARE_VALUE = 'R'
RARITY_SUPER_RARE_VALUE = 'SR'
RARITY_EXTENSION_RARE_VALUE = 'XR'
RARITY_TOKEN_VALUE = 'T'
RARITY_MARVEL_RARE_VALUE = 'MR'
RARITY_RULER_VALUE = 'RR'
RARITY_J_RULER_VALUE = 'JR'
RARITY_COLOSSAL_J_RULER_VALUE = 'JR*'
RARITY_NORMAL_VALUE = 'N'
RARITY_SECRET_RARE_VALUE = 'SEC'
RARITY_ASCENDED_RULER_VALUE = 'AR'
RARITY_ASCENDED_J_RULER_VALUE = 'JAR'

RARITY_CHOICE_VALUES = (
    (RARITY_COMMON_VALUE, RARITY_COMMON),
    (RARITY_UNCOMMON_VALUE, RARITY_UNCOMMON),
    (RARITY_RARE_VALUE, RARITY_RARE),
    (RARITY_SUPER_RARE_VALUE, RARITY_SUPER_RARE),
    (RARITY_EXTENSION_RARE_VALUE, RARITY_EXTENSION_RARE),
    (RARITY_TOKEN_VALUE, RARITY_TOKEN),
    (RARITY_MARVEL_RARE_VALUE, RARITY_MARVEL_RARE),
    (RARITY_RULER_VALUE, RARITY_RULER),
    (RARITY_J_RULER_VALUE, RARITY_J_RULER),
    (RARITY_COLOSSAL_J_RULER_VALUE, RARITY_COLOSSAL_J_RULER),
    (RARITY_NORMAL_VALUE, RARITY_NORMAL),
    #(RARITY_SECRET_RARE_VALUE, RARITY_SECRET_RARE),  We don't have any yet
    (RARITY_ASCENDED_RULER_VALUE, RARITY_ASCENDED_RULER),
    (RARITY_ASCENDED_J_RULER_VALUE, RARITY_ASCENDED_J_RULER)
)

CARD_TYPE_VALUES = [
    'Regalia',
    'Chant',
    'Rune',
    'Master Rune',
    'Magic Stone',
    'Basic Magic Stone',
    'Special Magic Stone',
    'True Magic Stone',
    'Ruler',
    'Basic J-Ruler',
    'J-Ruler'
    'Spell:Chant-Standby',
    'Resonator',
    'Sub-ruler',
    'Extension Rule',
]
CARD_SUBTYPE_VALUES = [
    'J',
    'Resonator',
    'Field',
    'Chant-Instant',
    'Stranger',
    'Shift'
]

FIRE_NAME = 'Fire'
WATER_NAME = 'Water'
DARKNESS_NAME = 'Darkness'
WIND_NAME = 'Wind'
LIGHT_NAME = 'Light'
VOID_NAME = 'Void'

ATTRIBUTE_NAMES = [
    FIRE_NAME,
    WATER_NAME,
    DARKNESS_NAME,
    WIND_NAME,
    LIGHT_NAME
]

ATTRIBUTE_FIRE_CODE = 'R'
ATTRIBUTE_WATER_CODE = 'U'
ATTRIBUTE_DARKNESS_CODE = 'B'
ATTRIBUTE_LIGHT_CODE = 'W'
ATTRIBUTE_WIND_CODE = 'G'
ATTRIBUTE_VOID_CODE = 'V'
WILL_MOON_CODE = 'M'
WILL_TIME_CODE = 'T'

ATTRIBUTE_CODES = [
    ATTRIBUTE_FIRE_CODE,
    ATTRIBUTE_WATER_CODE,
    ATTRIBUTE_DARKNESS_CODE,
    ATTRIBUTE_LIGHT_CODE,
    ATTRIBUTE_WIND_CODE
]

COLOUR_CHOICES = [
    (ATTRIBUTE_FIRE_CODE, FIRE_NAME),
    (ATTRIBUTE_WIND_CODE, WIND_NAME),
    (ATTRIBUTE_DARKNESS_CODE, DARKNESS_NAME),
    (ATTRIBUTE_LIGHT_CODE, LIGHT_NAME),
    (ATTRIBUTE_WATER_CODE, WATER_NAME),
    (ATTRIBUTE_VOID_CODE, VOID_NAME),
]

DOUBLE_SIDED_CARD_CHARACTER = '^'
J_SIDE_CHARACTER = 'J'
ALTERNATIVE_SIDE_CHARACTER = '*'
COLOSSAL_SIDE_CHARACTER = 'J^'

OTHER_SIDE_CHARACTERS = [  # Order is important for Card.other_sides
    COLOSSAL_SIDE_CHARACTER,
    DOUBLE_SIDED_CARD_CHARACTER,
    J_SIDE_CHARACTER,
    ALTERNATIVE_SIDE_CHARACTER,
]

# No longer used, refers to the query parameter on fowtcg.com when you search by a specific set.
# It is in sorted order from oldest to newest though, can be reused later
FOWTCG_CARD_DATABASE_SET_INDEX = {
    'CMF': 11,
    'TAT': 16,
    'MPR': 17,
    'MOA': 18,
    'VIN001': 19,
    'VS01': 7,
    'SKL': 8,
    'TTW': 9,
    'TMS': 13,
    'BFA': 14,
    'VIN002': 15,
    'SDL1': 3,
    'SDL2': 3,
    'SDL3': 3,
    'SDL4': 3,
    'SDL5': 3,
    'CFC': 2,
    'LEL': 4,
    'VIN003': 6,
    'RDE': 26,
    'ENW': 28,
    'SDR1': 29,
    'SDR2': 29,
    'SDR3': 29,
    'SDR4': 29,
    'SDR5': 29,
    'ACN': 30,
    'ADK': 31,
    'TSW': 34,
    'SDR6': 33,
    'WOM': 35,
    'SDV1': 38,
    'SDV2': 38,
    'SDV3': 38,
    'SDV4': 38,
    'SDV5': 38,
    'NDR': 37,
    'SNV': 39,
    'AOA': 40,
    'DBV': 41,
    'SDAO1': 43,
    'AO1': 42,
    'SDAO2': 45,
    'AO2': 44,
    'GITS2045SD': 47,
    'GITS2045': 48,
    'AO3': 46,
    'POFA': 49,
    'EDL': 50,
    'MSW': 51,
    'ROL': 52,
    'ADW': 53,
    'TST': 54,
    'PR': 20
}

SET_DATA = {
    'clusters': [
        {
            'name': 'Grimm',
            'sets': [
                {'code': 'CMF', 'name': "Crimson Moon's Fairy Tale"},
                {'code': 'TAT', 'name': "The Castle of Heaven and The Two Towers"},
                {'code': 'MPR', 'name': 'The Moon Priestess Returns'},
                {'code': 'MOA', 'name': "The Millennia of Ages"},
                {'code': 'VIN001', 'name': 'Vingolf "Engage Knights"'}
            ]
        },
        {
            'name': 'Alice',
            'sets': [
                {'code': 'VS01', 'name': "Faria, the Sacred Queen and Melgis, the Flame King"},
                {'code': 'SKL', 'name': 'The Seven Kings of the Lands'},
                {'code': 'TTW', 'name': 'The Twilight Wanderer'},
                {'code': 'TMS', 'name': 'The Moonlit Savior'},
                {'code': 'BFA', 'name': 'Battle for Attoractia'},
                {'code': 'VIN002', 'name': 'Vingolf "Valkyria Chronicles"'}
            ]
        },
        {
            'name': 'Lapis',
            'sets': [
                {'code': 'SDL1', 'name': 'Fairy Tale Force'},
                {'code': 'SDL2', 'name': "Rage of R'lyeh"},
                {'code': 'SDL3', 'name': 'Malefic Ice'},
                {'code': 'SDL4', 'name': 'Swarming Elves'},
                {'code': 'SDL5', 'name': 'Vampiric Hunger'},
                {'code': 'CFC', 'name': 'Curse of the Frozen Casket'},
                {'code': 'LEL', 'name': 'Legacy Lost'},
                {'code': 'VIN003', 'name': 'Vingolf "Ruler All Stars"'},
                {'code': 'RDE', 'name': 'Return of the Dragon Emperor'},
                {'code': 'ENW', 'name': 'Echoes of the New World'}
            ]
        },
        {
            'name': 'Reiya',
            'sets': [
                {'code': 'SDR1', 'name': 'King of the Mountain'},
                {'code': 'SDR2', 'name': 'Blood of the Dragons'},
                {'code': 'SDR3', 'name': 'Below the Waves'},
                {'code': 'SDR4', 'name': 'Elemental Surge'},
                {'code': 'SDR5', 'name': 'Children of the Night'},
                {'code': 'ACN', 'name': 'Ancient Nights'},
                {'code': 'ADK', 'name': 'Advent of the Demon King'},
                {'code': 'TSW', 'name': 'The Time Spinning Witch'},
                {'code': 'SDR6', 'name': 'The Lost Tomes'},
                {'code': 'WOM', 'name': 'Winds of the Ominous Moon'}
            ]
        },
        {
            'name': 'New Valhalla',
            'sets': [
                {'code': 'SDV1', 'name': 'New Valhalla Entry Set [Light] '},
                {'code': 'SDV2', 'name': 'New Valhalla Entry Set [Fire] '},
                {'code': 'SDV3', 'name': 'New Valhalla Entry Set [Water] '},
                {'code': 'SDV4', 'name': 'New Valhalla Entry Set [Wind] '},
                {'code': 'SDV5', 'name': 'New Valhalla Entry Set [Darkness] '},
                {'code': 'NDR', 'name': 'New Dawn Rises'},
                {'code': 'SNV', 'name': 'The Strangers of New Valhalla'},
                {'code': 'AOA', 'name': 'Awakening of the Ancients'},
                {'code': 'DBV', 'name': 'The Decisive Battle of Valhalla'}
            ]
        },
        {
            'name': 'Alice Origin',
            'sets': [
                {'code': 'SDAO1', 'name': 'Faria/Melgis'},
                {'code': 'AO1', 'name': 'Alice Origin'},
                {'code': 'SDAO2', 'name': 'Valentina/Pricia'},
                {'code': 'AO2', 'name': 'Alice Origin II'},
                {'code': 'GITS2045', 'name': 'GHOST IN THE SHELL SAC_2045'},
                {'code': 'GITS2045SD', 'name': 'Starter Deck GHOST IN THE SHELL SAC_2045'},
                {'code': 'AO3', 'name': 'Alice Origin III'},
                {'code': 'PofA', 'name': 'Prologue of Attoractia'},

            ]
        },
        {
            'name': 'Saga',
            'sets': [
                {'code': 'EDL', 'name': 'The Epic of the Dragon Lord'},
                {'code': 'MSW', 'name': 'The Magic Stone War - Zero'},
                {'code': 'ROL', 'name': 'Rebirth of Legend'},
                {'code': 'ADW', 'name': 'Assault into the Demonic World'},
                {'code': 'TST', 'name': 'The Seventh'}
            ]
        },
        {
            'name': 'Duel',
            'sets': [
                {'code': 'DSD', 'name': 'Duel Cluster Starter Decks'},
                {'code': 'GOG', 'name': 'Game of Gods'},
                {'code': 'GRL', 'name': 'Game of Gods Reloaded'},
                {'code': 'GRV', 'name': 'Game of Gods Revolution'}
            ]
        },
        {
            'name': 'Hero',
            'sets': [
                {'code': 'HSD', 'name': 'Hero Cluster Starter Decks'},
                {'code': 'NWE', 'name': 'A New World Emerges'},
                {'code': 'TUS', 'name': 'The Underworld of Secrets'},
                {'code': 'TWS', 'name': 'The War of the Suns'},
                {'code': 'CMB', 'name': 'Crimson Moon\'s Battleground'},
                {'code': 'ABC', 'name': 'Arcana Battle Colosseum'},
                {'code': 'CST', 'name': 'Clash of the Star Trees'}
            ]
        }
    ]
}

SET_CHOICES = []
for cluster in SET_DATA['clusters']:
    for fow_set in cluster['sets']:
        SET_CHOICES.append((fow_set['code'], f'{fow_set["name"]} ({fow_set["code"]})'))

SET_CHOICES.reverse()

TEXT_SEARCH_FIELD_CHOICES = [
    ('name', 'Name'),
    ('ability_texts__text', 'Abilities'),
    ('card_id', 'Set Code'),
    ('flavour', 'Flavour')
]
TOTAL_COST_CHOICES = listToChoices(list(range(0, 17)) + ['X'])

# Valhalla and Promos. Data exists in the database so we want to exclude it from.
# Checks 'startswith' so codes that will clash need trailing - if possible. Good luck otherwise :)
UNSEARCHED_DATABASE_SETS = [
    '1-',
    '2-',
    '3-',
    'S-',
]

DATABASE_CARD_TYPE_GROUPS = [
    {
        'name': 'Main Deck',
        'types': [
            'Addition',
            'Addition:Resonator',
            'Addition:Field',
            'Addition:J/Resonator',
            'Addition:Ruler/J-Ruler',
            'Chant',
            'Regalia',
            'Regalia (Shift)',
            'Resonator',
            'Resonator (Shift)',
            'Resonator (Stranger)',
            'Spell:Chant',
            'Spell:Chant-Instant',
            'Spell:Chant-Standby',
        ]
    },
    {
        'name': 'J/Ruler',
        'types': [
            'Ruler',
            'J-Ruler',
            'Order',
            'Sub-ruler',
            'Basic Ruler',
            'Basic J-Ruler',
        ]
    },
    {
        'name': 'Magic Stone Deck',
        'types': [
            'Basic Magic Stone',
            'Darkness Magic Stone',
            'Fire Magic Stone',
            'Light Magic Stone',
            'Magic Stone',
            'Special Magic Stone',
            'True Magic Stone',
            'Water Magic Stone',
            'Wind Magic Stone'
        ]
    },
    {
        'name': 'Other Decks',
        'types': [
            'Extension Rule',
            'Master Rune',
            'Rune',
        ]
    },
]

DATABASE_CARD_TYPE_CHOICES = []
for area in DATABASE_CARD_TYPE_GROUPS:
    for card_type in area['types']:
        DATABASE_CARD_TYPE_CHOICES.append((card_type, card_type))


CHIBI_NAMES = [
    'alhamaat',
    'charlotte',
    'faria',
    'fiethsing',
    'kaguya',
    'lapis',
    'lilias',
    'lumia',
    'mars',
    'merc',
    'mikage',
    'millium',
    'millium_dragon',
    'nyarlathotep',
    'pricia',
    'sol',
    'valentina',
    'wukong',
    'yog',
    'zero'
]

INFINITY_STRING = 'Inf'

DIVINITY_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (INFINITY_STRING, mark_safe('&infin;'))
]

ATK_DEF_COMPARATOR_CHOICES = [
    ('exact', '='),
    ('gt', mark_safe('&gt;')),
    ('lt', mark_safe('&lt;')),
]

TEXT_EXACT = 'Exact'
TEXT_CONTAINS_ALL = 'Contains all'
TEXT_CONTAINS_AT_LEAST_ONE = 'Contains at least one'

TEXT_EXACTNESS_OPTIONS = [
    (TEXT_EXACT, TEXT_EXACT),
    (TEXT_CONTAINS_ALL, TEXT_CONTAINS_ALL),
    (TEXT_CONTAINS_AT_LEAST_ONE, TEXT_CONTAINS_AT_LEAST_ONE)
]

DATABASE_SORT_BY_MOST_RECENT = 'Most Recent'
DATABASE_SORT_BY_TOTAL_COST = 'Increasing Total Cost'
DATABASE_SORT_BY_ALPHABETICAL = 'Alphabetically'
DATABASE_SORT_BY_CHOICES = [
    (DATABASE_SORT_BY_MOST_RECENT, DATABASE_SORT_BY_MOST_RECENT),
    (DATABASE_SORT_BY_TOTAL_COST, DATABASE_SORT_BY_TOTAL_COST),
    (DATABASE_SORT_BY_ALPHABETICAL, DATABASE_SORT_BY_ALPHABETICAL),
]

DATABASE_COLOUR_MATCH_ALL = 'All'
DATABASE_COLOUR_MATCH_ANY = 'Any'
DATABASE_COLOUR_MATCH_ONLY = 'Only'
DATABASE_COLOUR_MATCH_EXACT = 'Exact'
DATABASE_COLOUR_MATCH_CHOICES = [
    (DATABASE_COLOUR_MATCH_ANY, 'Any selected color'),
    (DATABASE_COLOUR_MATCH_ALL, 'All selected colors'),
    (DATABASE_COLOUR_MATCH_ONLY, 'Only selected colors'),
    (DATABASE_COLOUR_MATCH_EXACT, 'Exact colors selected'),
]

DATABASE_COLOUR_COMBINATION_MULTI = 'Multi'
DATABASE_COLOUR_COMBINATION_MONO = 'Mono'
DATABASE_COLOUR_COMBINATION_CHOICES = [
    (DATABASE_COLOUR_COMBINATION_MULTI, 'Multi color only'),
    (DATABASE_COLOUR_COMBINATION_MONO, 'Single color only')
]

SETS_IN_ORDER = [
    'PR',  # Promos
    'BSR',  # Basic Rulers
    'CMF',
    'TAT',
    'MPR',
    'MOA',
    'VIN001',
    'VS01',
    'SKL',
    'TTW',
    'TMS',
    'BFA',
    'VIN002',
    'SDL1',
    'SDL2',
    'SDL3',
    'SDL4',
    'SDL5',
    'CFC',
    'LEL',
    'VIN003',
    'RDE',
    'ENW',
    'SDR1',
    'SDR2',
    'SDR3',
    'SDR4',
    'SDR5',
    'ACN',
    'ADK',
    'TSW',
    'SDR6',
    'WOM',
    'SDV1',
    'SDV2',
    'SDV3',
    'SDV4',
    'SDV5',
    'NDR',
    'AO2 Buy a BoxJ',
    'SNV',
    'AOA V3 Buy 2',
    'AOA',
    'DBV',
    'SDAO1',
    'AO1 Buy a Box',
    'AO1 Buy a BoxJ',
    'AO1',
    'SDAO2',
    'AO2 Buy a Box',
    'AO2',
    'GITS2045SD',
    'GITS2045',
    'SOUVENIR038',
    'SOUVENIR039',
    'AO3 Buy a Box',
    'AO3',
    'AO4 Buy a Box',
    'PofA',
    'PofAMS',
    'EDL',
    'MSW',
    'ROL',
    'ADW',
    'TST',
    'DSD',
    'GOG',
    'D2 Buy a Box',
    'D2 Prerelease Party',
    'GRL',
    'D3 Buy a Box',
    'D3 Prerelease Party',
    'GRV',
    'HSD',
    'NWE',
    'TUS',
    'H2 Buy a Box',
    'H2 Prerelease Party',
    'TWS',
    'H3 Buy a Box',
    'H3 Prerelease Party',
    'CMB',
    'H4 Buy a Box',
    'H4 Prerelease Party',
    'ABC',
    'H5 Buy a Box',
    'H5 Prerelease Party',
    'CST',
    'MC02',  # Memoria Collection
]

SEARCH_CARD_TYPES_INCLUDE = {
    'Addition': [
        'Addition:Field',
        'Addition: Field',
        'Addition:Resonator',
        'Addition:J/Resonator',
        'Addition:Ruler/J-ruler'
    ],
    'Addition:Field': [
        'Addition: Field'
    ],
    'Resonator': [
        'Resonator (Shift)',
        'Resonator (Stranger)'
    ],
    'Chant': [
        'Spell:Chant',
        'Spell:Chant-Instant',
        'Spell:Chant-Standby'
    ],
    'Regalia': [
        'Regalia (Shift)'
    ],
    'Ruler': [
        'Basic Ruler'
    ],
    'J-Ruler': [
        'Basic J-Ruler'
    ],
    'Basic Magic Stone': [
        'Darkness Magic Stone',
        'Fire Magic Stone',
        'Light Magic Stone',
        'Water Magic Stone',
        'Wind Magic Stone'
    ],
    'Magic Stone': [
        'Basic Magic Stone',
        'Darkness Magic Stone',
        'Fire Magic Stone',
        'Light Magic Stone',
        'Special Magic Stone',
        'True Magic Stone',
        'Water Magic Stone',
        'Wind Magic Stone'
    ],
    'Rune': [
        'Master Rune'
    ]
}

SEARCH_SETS_INCLUDE = {
    'AOA': [
        'AOA V3 Buy 2'
    ],
    'AO1': [
        'AO1 Buy a Box',
        'AO1 Buy a BoxJ'
        ],
    'AO2': [
        'AO2 Buy a Box',
        'AO2 Buy a BoxJ'
    ],
    'AO3': [
        'AO3 Buy a Box',
        'AO3 Buy a BoxJ'
    ],
    'PofA': [
        'AO4 Buy a Box',
        'AO4 Buy a BoxJ'
    ],
    'GRL': [
        'D2 Buy a Box',
        'D2 Prerelease Party'
    ],
    'GRV': [
        'D3 Prerelease Party',
        'D3 Buy a Box'
    ],
    'TUS': [
        'H2 Buy a Box',
        'H2 Prerelease Party'
    ],
    'TWS': [
        'H3 Buy a Box',
        'H3 Prerelease Party'
    ],
    'CMB': [
        'H4 Prerelease Party',
        'H4 Buy a Box'
    ],
    'CST': [
        'H5 Buy a Box',
        'H5 Prerelease Party',
        'MC02'
    ]
}

KEYWORDS_CHOICES = [
    ('[Tales]', 'Tales'),
    ('[Villains]', 'Villains'),
    ('[Precision]', 'Precision'),
    ('[Flying]', 'Flying'),
    ('[Explode]', 'Explode'),
    ('[First Strike]', 'First Strike'),
    ('[Swiftness]', 'Swiftness'),
    ('[Imperishable]', 'Imperishable'),
    ('[Quickcast]', 'Quickcast'),
    ('[Remnant]', 'Remnant'),
    ('[Barrier]', 'Barrier'),
    ('[Will of Despair]', 'Will of Despair'),
    ('[Will of Hope]', 'Will of Hope'),
    ('[Seal]', 'Seal'),
    ('[Drain]', 'Drain'),
    ('[Null]', 'Null'),
    ('[Drain]', 'Drain'),
    ('[Bloodlust]', 'Bloodlust'),
    ('[Pierce]', 'Pierce'),
    ('[Barrier]', 'Barrier'),
    ('[Divinity]', 'Divinity'),
    ('[Bane]', 'Bane'),
    ('[Rune]', 'Rune'),
    ('[Mythic]', 'Mythic'),
    ('[Eternal]', 'Eternal'),
    ('[Limit Break]', 'Limit Break'),
    ('[Revenge]', 'Revenge'),
    ('[Fallen]', 'Fallen'),
    ('[Revolution]', 'Revolution'),
    ('[Awakening]', 'Awakening'),
    ('[Incarnation]', 'Incarnation'),
    ('God\'s Art', 'God\'s Art'),
    ('[Trigger]', 'Trigger'),
    ('[Stealth]', 'Stealth'),
    ('[Evolution]', 'Evolution'),
    ('[Shift]', 'Shift'),
    ('[Limit]', 'Limit'),
    ('[Energize]', 'Energize'),
    ('[Bestow]', 'Bestow'),
    ('[Mana]', 'Mana'),
    ('[Torrent]', 'Torrent'),
    ('[Judgment]', 'Judgment'),
    ('[Inheritance]', 'Inheritance'),
    ('[Resonance]', 'Resonance'),
    ('[Mobilize]', 'Mobilize'),
    ('Sealed Item', 'Sealed Item'),
    ('[Crest]', 'Crest'),
    ('[Grimoire]', 'Grimoire'),
    ('[Legend]', 'Legend'),
    ('[Enter]', 'Enter'),
    ('[Faith]', 'Faith'),
    ('[Stranger]', 'Stranger'),
    ('[Target Attack]', 'Target Attack'),
    ('[Dive]', 'Dive'),
    ('[Tag]', 'Tag'),
    ('[Guidance]', 'Guidance'),
    ('[Revolution Order]', 'Revolution Order'),
    ('[Revolution]', 'Revolution'),
    ('[Force Command]', 'Force Command'),
    ('[Force Resonance]', 'Force Resonance'),
    ('[Dragon Emblem]', 'Dragon Emblem'),
    ('[Force]', 'Force'),
    ('[Union Seven <Machine>]', 'Union Seven <Machine>'),
    ('[Union Seven <New Twelve Olympian Gods>]', 'Union Seven <New Twelve Olympian Gods>'),
    ('[Convoke]', 'Convoke')
]


ZONES_SHOWN_BY_DEFAULT = [
    'Ruler Area',
    'Main Deck',
    'Magic Stone Deck',
    'Side Deck'
]

SITE_ICON_URL = static('img/wind.png')

FORMATS = [
    'Wanderer'
]

BANNED_CARDS = [
    {
        'format_name': 'Wanderer',
        'cards': [
            'EDL-064',
            'TST-063',
            'GOG-031',
            'TTW-006',
            'TMS-094',
            'TTW-099',
            'TST-024',
            'CFC-037',  # Hook is also BAB promo but not in the DB
            'ENW-049',
            'ENW-051',
            'MSW-053',
            'SDV4-005',
            'DBV-062',  # Reprint of SDV4-005
            'CMF-069',
            'CMF-071',
            'VIN001-054',  # Reprint of CMF-071
            'EDL-062',
            'ADK-106',
            'ENW-063',
            'TSW-109',
            'TSW-109J',
            'ADK-113',
            'TMS-064',  # Also WL005 promo (wall of wind)
            'ENW-074',
            'DBV-079',
            'AOA-100',
            'DBV-092',
            'TST-075',
            'DBV-095',
            'AO3-082',
            'MSW-102'
        ],
        'combination_bans':[
            ['TAT-090', 'GRV-085'],
            ['TTW-064', 'ROL-017'],
            ['TTW-097', 'GRL-006'],
            ['TSW-094', 'GRV-082'],
            ['TSW-149', 'GRV-026'],
            ['ACN-096', 'GRL-034'],
            ['AO3-046', 'PofA-111'],
            ['EDL-076', 'EDL-096'],
            ['EDL-074', 'ROL-018'],
            ['MSW-002', 'MSW-042'],
            ['MSW-026', 'MSW-073'],
            ['MSW-042', 'MSW-026'],
            ['ROL-013', 'ADW-030'],
            ['ADW-003', 'ADW-026'],
            ['ADW-016', 'ADW-020'],
            ['TST-067', 'TST-073'],
            ['TST-078', 'GRV-060'],
            ['DSD-006', 'DSD-008'],
            ['GOG-023', 'GOG-024'],
            ['GOG-050', 'GOG-078'],
            ['GRL-067', 'GRL-083'],
            ['GRL-030', 'GRL-038'],
            ['GRV-051', 'GRV-070'],
            ['GRV-064', 'GRV-085']
        ]
    }
]

PICK_PERIOD_DAYS = [  # Also includes "all time" when created in importMetricPeriods
    7,
    30,
    90
]