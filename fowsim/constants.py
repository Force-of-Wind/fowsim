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
    (RARITY_TOKEN_VALUE, RARITY_TOKEN),
    (RARITY_MARVEL_RARE_VALUE, RARITY_MARVEL_RARE),
    (RARITY_RULER_VALUE, RARITY_RULER),
    (RARITY_J_RULER_VALUE, RARITY_J_RULER),
    (RARITY_COLOSSAL_J_RULER_VALUE, RARITY_COLOSSAL_J_RULER),
    (RARITY_NORMAL_VALUE, RARITY_NORMAL),
    (RARITY_SECRET_RARE_VALUE, RARITY_SECRET_RARE),
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
    'Resonator'
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

# No longer used, refers to the query parameter on fowtcg.com when you search by a specific set
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
                {'code': 'VIN003', 'name': 'Vingolf "Ruler All Stars'},
                {'code': 'RDE', 'name': 'Return of the Dragon Emperor'},
                {'code': 'ENW', 'name': 'Echoes of the New World'}
            ]
        },
        {
            'name': 'Reiya',
            'sets':[
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
                {'code': 'POFA', 'name': 'Prologue of Attoractia'},

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
        }
    ]
}

SET_CHOICES = []
for cluster in SET_DATA['clusters']:
    for fow_set in cluster['sets']:
        SET_CHOICES.append((fow_set['code'], fow_set['name']))

SET_CHOICES.reverse()

TEXT_SEARCH_FIELD_CHOICES = [
    ('name', 'Name'),
    ('races__name', 'Race/Trait'),
    ('ability_texts__text', 'Abilities')
]
TOTAL_COST_CHOICES = listToChoices(list(range(0, 13)) + ['X'])

# Valhalla and Promos. Data exists in the database so we want to exclude it from
UNSUPPORTED_DATABASE_SETS = [
    'AO2 Buy a Box',
    'AO2 Buy a BoxJ',
    'SOUVENIR038',
    'SOUVENIR039',
    'AOA V3 Buy 2',
    'AO1 Buy a BoxJ'
    'AO3 Buy a Box',
    '1',
    '2'
    '3',
    'S'
]

DATABASE_CARD_TYPE_CHOICES = listToChoices([
    'Addition',
    'Addition: Field',
    'Addition:Field',
    'Addition:J',
    'Addition:Resonator',
    'Basic J-Ruler',
    'Basic Magic Stone',
    'Basic Ruler',
    'Chant',
    'J-Ruler',
    'Magic Stone',
    'Master Rune',
    'Regalia',
    'Regalia (Shift)',
    'Resonator',
    'Resonator (Shift)',
    'Resonator (Stranger)',
    'Ruler',
    'Rune',
    'Special Magic Stone',
    'Spell:Chant',
    'Spell:Chant-Instant',
    'Spell:Chant-Standby',
    'True Magic Stone'
])
