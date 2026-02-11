from django.utils.safestring import mark_safe
from django.templatetags.static import static

from fowsim.utils import listToChoices

CARD_POSITION_TOP = "Top"
CARD_POSITION_BOTTOM = "Bottom"
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

RARITY_COMMON = "Common"
RARITY_UNCOMMON = "Uncommon"
RARITY_RARE = "Rare"
RARITY_SUPER_RARE = "Super Rare"
RARITY_EXTENSION_RARE = "Extension Rare"
RARITY_TOKEN = "Token"
RARITY_MARVEL_RARE = "Marvel Rare"
RARITY_RULER = "Ruler"
RARITY_J_RULER = "J-Ruler"
RARITY_COLOSSAL_J_RULER = "Colossal J-Ruler"
RARITY_NORMAL = "Normal"
RARITY_SECRET_RARE = "Secret Rare"
RARITY_ASCENDED_RULER = "Ascended Ruler"
RARITY_ASCENDED_J_RULER = "Ascended J-ruler"
RARITY_SUB_RULER_RARE = "Sub-Ruler"

RARITY_COMMON_VALUE = "C"
RARITY_UNCOMMON_VALUE = "U"
RARITY_RARE_VALUE = "R"
RARITY_SUPER_RARE_VALUE = "SR"
RARITY_EXTENSION_RARE_VALUE = "XR"
RARITY_TOKEN_VALUE = "T"
RARITY_MARVEL_RARE_VALUE = "MR"
RARITY_RULER_VALUE = "RR"
RARITY_J_RULER_VALUE = "JR"
RARITY_COLOSSAL_J_RULER_VALUE = "JR*"
RARITY_NORMAL_VALUE = "N"
RARITY_SECRET_RARE_VALUE = "SEC"
RARITY_ASCENDED_RULER_VALUE = "AR"
RARITY_ASCENDED_J_RULER_VALUE = "JAR"
RARITY_SUB_RULER_VALUE = "SRR"

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
    (RARITY_SECRET_RARE_VALUE, RARITY_SECRET_RARE),
    (RARITY_ASCENDED_RULER_VALUE, RARITY_ASCENDED_RULER),
    (RARITY_ASCENDED_J_RULER_VALUE, RARITY_ASCENDED_J_RULER),
    (RARITY_SUB_RULER_VALUE, RARITY_SUB_RULER_RARE),
)

CARD_TYPE_RULER = "Ruler"

CARD_TYPE_VALUES = [
    "Regalia",
    "Chant",
    "Rune",
    "Master Rune",
    "Magic Stone",
    "Basic Magic Stone",
    "Special Magic Stone",
    "True Magic Stone",
    "Ruler",
    "Basic J-Ruler",
    "J-Ruler",
    "Spell:Chant-Standby",
    "Resonator",
    "Sub-Ruler",
    "Extension Rule",
    "Warden",
    "Darkness Magic Stone",
    "Fire Magic Stone",
    "Light Magic Stone",
    "Water Magic Stone",
    "Wind Magic Stone",
    "Void Magic Stone",
]
CARD_SUBTYPE_VALUES = ["J", "Resonator", "Field", "Chant-Instant", "Stranger", "Shift"]

FIRE_NAME = "Fire"
WATER_NAME = "Water"
DARKNESS_NAME = "Darkness"
WIND_NAME = "Wind"
LIGHT_NAME = "Light"
VOID_NAME = "Void"
MOON_NAME = "Moon"
TIME_NAME = "Time"

ATTRIBUTE_NAMES = [FIRE_NAME, WATER_NAME, DARKNESS_NAME, WIND_NAME, LIGHT_NAME]

ATTRIBUTE_FIRE_CODE = "R"
ATTRIBUTE_WATER_CODE = "U"
ATTRIBUTE_DARKNESS_CODE = "B"
ATTRIBUTE_LIGHT_CODE = "W"
ATTRIBUTE_WIND_CODE = "G"
ATTRIBUTE_VOID_CODE = "V"
WILL_MOON_CODE = "M"
WILL_TIME_CODE = "T"

ATTRIBUTE_CODES = [
    ATTRIBUTE_FIRE_CODE,
    ATTRIBUTE_WATER_CODE,
    ATTRIBUTE_DARKNESS_CODE,
    ATTRIBUTE_LIGHT_CODE,
    ATTRIBUTE_WIND_CODE,
]

COLOUR_CHOICES = [
    (ATTRIBUTE_LIGHT_CODE, LIGHT_NAME),
    (ATTRIBUTE_FIRE_CODE, FIRE_NAME),
    (ATTRIBUTE_WATER_CODE, WATER_NAME),
    (ATTRIBUTE_WIND_CODE, WIND_NAME),
    (ATTRIBUTE_DARKNESS_CODE, DARKNESS_NAME),
    (ATTRIBUTE_VOID_CODE, VOID_NAME),
]

CHARACTERISTIC_CHOICES = [
    (WILL_MOON_CODE, MOON_NAME),
    (WILL_TIME_CODE, TIME_NAME),
]

DOUBLE_SIDED_CARD_CHARACTER = "^"
J_SIDE_CHARACTER = "J"
ALTERNATIVE_SIDE_CHARACTER = "*"
COLOSSAL_SIDE_CHARACTER = "J^"

OTHER_SIDE_CHARACTERS = [  # Order is important for Card.other_sides
    COLOSSAL_SIDE_CHARACTER,
    DOUBLE_SIDED_CARD_CHARACTER,
    J_SIDE_CHARACTER,
    ALTERNATIVE_SIDE_CHARACTER,
]

# No longer used, refers to the query parameter on fowtcg.com when you search by a specific set.
# It is in sorted order from oldest to newest though, can be reused later
FOWTCG_CARD_DATABASE_SET_INDEX = {
    "CMF": 11,
    "TAT": 16,
    "MPR": 17,
    "MOA": 18,
    "VIN001": 19,
    "VS01": 7,
    "SKL": 8,
    "TTW": 9,
    "TMS": 13,
    "BFA": 14,
    "VIN002": 15,
    "SDL1": 3,
    "SDL2": 3,
    "SDL3": 3,
    "SDL4": 3,
    "SDL5": 3,
    "CFC": 2,
    "LEL": 4,
    "VIN003": 6,
    "RDE": 26,
    "ENW": 28,
    "SDR1": 29,
    "SDR2": 29,
    "SDR3": 29,
    "SDR4": 29,
    "SDR5": 29,
    "ACN": 30,
    "ADK": 31,
    "TSW": 34,
    "SDR6": 33,
    "WOM": 35,
    "SDV1": 38,
    "SDV2": 38,
    "SDV3": 38,
    "SDV4": 38,
    "SDV5": 38,
    "NDR": 37,
    "SNV": 39,
    "AOA": 40,
    "DBV": 41,
    "SDAO1": 43,
    "AO1": 42,
    "SDAO2": 45,
    "AO2": 44,
    "GITS2045SD": 47,
    "GITS2045": 48,
    "AO3": 46,
    "POFA": 49,
    "EDL": 50,
    "MSW": 51,
    "ROL": 52,
    "ADW": 53,
    "TST": 54,
    "PR": 20,
}

SET_DATA = {
    "clusters": [
        {
            "name": "Promo",
            "sets": [
                {"code": "WL", "name": "Wanderer League"},
                {"code": "RL", "name": "Ruler League"},
                {"code": "World", "name": "World's Rewards"},
                {"code": "WGP", "name": "World Grand Prix"},
                {"code": "WPR", "name": "Will Power Rewards"},
                {"code": "BaB", "name": "Buy a Box"},
                {"code": "Pre", "name": "Pre-release Party"},
                {"code": "PR2015", "name": "2015 Promo"},
                {"code": "Souvenir", "name": "Souvenir"},
                {"code": "Judge", "name": "Judge"},
            ],
        },
        {
            "name": "Arcana Battle Colosseum",
            "sets": [
                {"code": "ABC", "name": "Arcana Battle Colosseum"},
                {"code": "ABC-WB", "name": "ABC 2023 Light & Water"},
                {"code": "ABC-WD", "name": "ABC 2023 Light & Darkness"},
                {"code": "ABC-RG", "name": "ABC 2023 Fire & Wind"},
                {"code": "ABC-RD", "name": "ABC 2023 Fire & Darkness"},
                {"code": "ABC-BG", "name": "ABC 2023 Water & Wind"},
                {"code": "ABC-SD01", "name": "Elektra vs The Lich King (Elektra)"},
                {"code": "ABC-SD02", "name": "Replicant: Aritstella vs Ki Lua (Replicant: Aristella)"},
                {"code": "ABC-SD03", "name": "Gnome vs Reinhardt (Gnome)"},
                {"code": "ABC-SD04", "name": "Hyde vs Undine (Hyde)"},
                {"code": "ABC-SD05", "name": "Hyde vs Undine (Undine)"},
                {"code": "ABC-SD06", "name": "Replicant: Aritstella vs Ki Lua (Ki Lua)"},
                {"code": "ABC-SD07", "name": "Efreet vs Falchion (Efreet)"},
                {"code": "ABC-SD08", "name": "Efreet vs Falchion (Falchion)"},
                {"code": "ABC-SD09", "name": "Gnome vs Reinhardt (Reinhardt)"},
                {"code": "ABC-SD10", "name": "Elektra vs The Lich King (The Lich King)"},
                {"code": "ABC-SD11", "name": "Void vs Void"},
            ],
        },
        {
            "name": "Extra Sets",
            "sets": [
                {"code": "VIN001", "name": 'Vingolf "Engage Knights"'},
                {"code": "VIN002", "name": 'Vingolf "Valkyria Chronicles"'},
                {"code": "VIN003", "name": 'Vingolf "Ruler All Stars"'},
                {"code": "GITS2045", "name": "GHOST IN THE SHELL SAC_2045"},
                {"code": "GITS2045SD", "name": "Starter Deck GHOST IN THE SHELL SAC_2045"},
                {"code": "ATD", "name": "Antechamber of the Ten Dimensions"},
            ],
        },
        {
            "name": "Grimm",
            "sets": [
                {"code": "CMF", "name": "Crimson Moon's Fairy Tale"},
                {"code": "TAT", "name": "The Castle of Heaven and The Two Towers"},
                {"code": "MPR", "name": "The Moon Priestess Returns"},
                {"code": "MOA", "name": "The Millennia of Ages"},
            ],
        },
        {
            "name": "Alice",
            "sets": [
                {"code": "VS01", "name": "Faria, the Sacred Queen and Melgis, the Flame King"},
                {"code": "SKL", "name": "The Seven Kings of the Lands"},
                {"code": "TTW", "name": "The Twilight Wanderer"},
                {"code": "TMS", "name": "The Moonlit Savior"},
                {"code": "BFA", "name": "Battle for Attoractia"},
            ],
        },
        {
            "name": "Lapis",
            "sets": [
                {"code": "SDL1", "name": "Fairy Tale Force"},
                {"code": "SDL2", "name": "Rage of R'lyeh"},
                {"code": "SDL3", "name": "Malefic Ice"},
                {"code": "SDL4", "name": "Swarming Elves"},
                {"code": "SDL5", "name": "Vampiric Hunger"},
                {"code": "CFC", "name": "Curse of the Frozen Casket"},
                {"code": "LEL", "name": "Legacy Lost"},
                {"code": "RDE", "name": "Return of the Dragon Emperor"},
                {"code": "ENW", "name": "Echoes of the New World"},
            ],
        },
        {
            "name": "Reiya",
            "sets": [
                {"code": "SDR1", "name": "King of the Mountain"},
                {"code": "SDR2", "name": "Blood of the Dragons"},
                {"code": "SDR3", "name": "Below the Waves"},
                {"code": "SDR4", "name": "Elemental Surge"},
                {"code": "SDR5", "name": "Children of the Night"},
                {"code": "ACN", "name": "Ancient Nights"},
                {"code": "ADK", "name": "Advent of the Demon King"},
                {"code": "TSW", "name": "The Time Spinning Witch"},
                {"code": "SDR6", "name": "The Lost Tomes"},
                {"code": "WOM", "name": "Winds of the Ominous Moon"},
            ],
        },
        {
            "name": "New Valhalla",
            "sets": [
                {"code": "SDV1", "name": "New Valhalla Entry Set [Light] "},
                {"code": "SDV2", "name": "New Valhalla Entry Set [Fire] "},
                {"code": "SDV3", "name": "New Valhalla Entry Set [Water] "},
                {"code": "SDV4", "name": "New Valhalla Entry Set [Wind] "},
                {"code": "SDV5", "name": "New Valhalla Entry Set [Darkness] "},
                {"code": "NDR", "name": "New Dawn Rises"},
                {"code": "SNV", "name": "The Strangers of New Valhalla"},
                {"code": "AOA", "name": "Awakening of the Ancients"},
                {"code": "DBV", "name": "The Decisive Battle of Valhalla"},
            ],
        },
        {
            "name": "Alice Origin",
            "sets": [
                {"code": "SDAO1", "name": "Faria/Melgis"},
                {"code": "AO1", "name": "Alice Origin"},
                {"code": "SDAO2", "name": "Valentina/Pricia"},
                {"code": "AO2", "name": "Alice Origin II"},
                {"code": "AO3", "name": "Alice Origin III"},
                {"code": "PofA", "name": "Prologue of Attoractia"},
            ],
        },
        {
            "name": "Saga",
            "sets": [
                {"code": "EDL", "name": "The Epic of the Dragon Lord"},
                {"code": "MSW", "name": "The Magic Stone War - Zero"},
                {"code": "ROL", "name": "Rebirth of Legend"},
                {"code": "ADW", "name": "Assault into the Demonic World"},
                {"code": "TST", "name": "The Seventh"},
            ],
        },
        {
            "name": "Duel",
            "sets": [
                {"code": "DSD", "name": "Duel Cluster Starter Decks"},
                {"code": "GOG", "name": "Game of Gods"},
                {"code": "GRL", "name": "Game of Gods Reloaded"},
                {"code": "GRV", "name": "Game of Gods Revolution"},
            ],
        },
        {
            "name": "Hero",
            "sets": [
                {"code": "HSD", "name": "Hero Cluster Starter Decks"},
                {"code": "NWE", "name": "A New World Emerges"},
                {"code": "TUS", "name": "The Underworld of Secrets"},
                {"code": "TWS", "name": "The War of the Suns"},
                {"code": "CMB", "name": "Crimson Moon's Battleground"},
                {"code": "CST", "name": "Clash of the Star Trees"},
                {"code": "JRP", "name": "Judgment of the Rogue Planet"},
            ],
        },
        {
            "name": "Trinity",
            "sets": [
                {"code": "TSD1", "name": "Lehen Deck"},
                {"code": "TSD2", "name": "Yokoshima Deck"},
                {"code": "TTT", "name": "Thoth of the Trinity"},
                {"code": "TSR", "name": "The Battle at the Sacred Ruins"},
                {"code": "TEU", "name": "Timeless Eclipse of the Underworld"},
                {"code": "TOP", "name": "Ten Oaths of Protopaterpolis' War"},
            ],
        },
        {
            "name": "Masterpiece Collection",
            "sets": [
                {"code": "MP01", "name": 'Masterpiece "Pilgrim Memories"'},
                {"code": "MP02", "name": 'Masterpiece Collection 02 "Fates Reunited!"'},
                {"code": "MP03", "name": 'Masterpiece Collection 03 "Dimensional Hope"'},
            ],
        },
        {
            "name": "Evil",
            "sets": [
                {"code": "ESD1", "name": "Valgott Deck"},
                {"code": "ESD2", "name": "Metelda Deck"},
                {"code": "DRC", "name": "Descent into the Raven's Catacombs"},
                {"code": "JRV", "name": "Journey to Ravidra"},
            ],
        },
    ]
}

SET_CHOICES = []
for cluster in SET_DATA["clusters"]:
    for fow_set in cluster["sets"]:
        SET_CHOICES.append((fow_set["code"], f'{fow_set["name"]} ({fow_set["code"]})'))

SET_CHOICES.reverse()

TEXT_SEARCH_FIELD_CHOICES = [
    ("name", "Name"),
    ("ability_texts__text", "Abilities"),
    ("card_id", "Set Code"),
    ("flavour", "Flavour"),
]
TOTAL_COST_CHOICES = listToChoices(list(range(0, 17)) + ["X"])

# Valhalla and Promos. Data exists in the database so we want to exclude it from.
# Checks 'startswith' so codes that will clash need trailing - if possible. Good luck otherwise :)
UNSEARCHED_DATABASE_SETS = [
    "1-",
    "2-",
    "3-",
    "S-",
]

DATABASE_CARD_TYPE_GROUPS = [
    {
        "name": "Main Deck",
        "types": [
            "Addition",
            "Addition:Resonator",
            "Addition:Field",
            "Addition:J/Resonator",
            "Addition:Ruler/J-Ruler",
            "Chant",
            "Chant/Rune",
            "Chant/Master Rune",
            "Regalia",
            "Regalia (Shift)",
            "Resonator",
            "Resonator (Shift)",
            "Resonator (Stranger)",
            "Spell:Chant",
            "Spell:Chant-Instant",
            "Spell:Chant-Standby",
            "Warden",
        ],
    },
    {
        "name": "J/Ruler",
        "types": [
            "Ruler",
            "J-Ruler",
            "Order",
            "Sub-Ruler",
            "Basic Ruler",
            "Basic J-Ruler",
        ],
    },
    {
        "name": "Magic Stone Deck",
        "types": [
            "Basic Magic Stone",
            "Darkness Magic Stone",
            "Fire Magic Stone",
            "Light Magic Stone",
            "Magic Stone",
            "Special Magic Stone",
            "True Magic Stone",
            "Water Magic Stone",
            "Wind Magic Stone",
            "Void Magic Stone",
        ],
    },
    {
        "name": "Other Decks",
        "types": [
            "Extension Rule",
            "Master Rune",
            "Rune",
        ],
    },
]

DATABASE_CARD_TYPE_CHOICES = []
for area in DATABASE_CARD_TYPE_GROUPS:
    for card_type in area["types"]:
        DATABASE_CARD_TYPE_CHOICES.append((card_type, card_type))


CHIBI_NAMES = [
    "alhamaat",
    "charlotte",
    "faria",
    "fiethsing",
    "kaguya",
    "lapis",
    "lilias",
    "lumia",
    "mars",
    "merc",
    "mikage",
    "millium",
    "millium_dragon",
    "nyarlathotep",
    "pricia",
    "sol",
    "valentina",
    "wukong",
    "yog",
    "zero",
]

INFINITY_STRING = "Inf"

DIVINITY_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
    (INFINITY_STRING, mark_safe("&infin;")),
]

ATK_DEF_COMPARATOR_CHOICES = [
    ("exact", "="),
    ("gt", mark_safe("&gt;")),
    ("lt", mark_safe("&lt;")),
]

TEXT_EXACT = "Exact"
TEXT_CONTAINS_ALL = "Contains all"
TEXT_CONTAINS_AT_LEAST_ONE = "Contains at least one"

TEXT_EXACTNESS_OPTIONS = [
    (TEXT_EXACT, TEXT_EXACT),
    (TEXT_CONTAINS_ALL, TEXT_CONTAINS_ALL),
    (TEXT_CONTAINS_AT_LEAST_ONE, TEXT_CONTAINS_AT_LEAST_ONE),
]

DATABASE_SORT_BY_MOST_RECENT = "Most Recent"
DATABASE_SORT_BY_TOTAL_COST = "Increasing Total Cost"
DATABASE_SORT_BY_ALPHABETICAL = "Alphabetically"
DATABASE_SORT_BY_POPULARITY = "Popularity"
DATABASE_SORT_BY_CHOICES = [
    (DATABASE_SORT_BY_MOST_RECENT, DATABASE_SORT_BY_MOST_RECENT),
    (DATABASE_SORT_BY_TOTAL_COST, DATABASE_SORT_BY_TOTAL_COST),
    (DATABASE_SORT_BY_ALPHABETICAL, DATABASE_SORT_BY_ALPHABETICAL),
    (DATABASE_SORT_BY_POPULARITY, DATABASE_SORT_BY_POPULARITY),
]

DATABASE_COLOUR_MATCH_ALL = "All"
DATABASE_COLOUR_MATCH_ANY = "Any"
DATABASE_COLOUR_MATCH_ONLY = "Only"
DATABASE_COLOUR_MATCH_EXACT = "Exact"
DATABASE_COLOUR_MATCH_CHOICES = [
    (DATABASE_COLOUR_MATCH_ANY, "Any selected color"),
    (DATABASE_COLOUR_MATCH_ALL, "All selected colors"),
    (DATABASE_COLOUR_MATCH_ONLY, "Only selected colors"),
    (DATABASE_COLOUR_MATCH_EXACT, "Exact colors selected"),
]

DATABASE_COLOUR_COMBINATION_MULTI = "Multi"
DATABASE_COLOUR_COMBINATION_MONO = "Mono"
DATABASE_COLOUR_COMBINATION_CHOICES = [
    (DATABASE_COLOUR_COMBINATION_MULTI, "Multi color only"),
    (DATABASE_COLOUR_COMBINATION_MONO, "Single color only"),
]

# Decklist Sorting
DECKLIST_SORT_BY_LAST_MODIFIED = "last_modified"
DECKLIST_SORT_BY_NAME = "name"
DECKLIST_SORT_BY_CARD_COUNT = "card_count"

DECKLIST_SORT_BY_CHOICES = [
    (DECKLIST_SORT_BY_LAST_MODIFIED, "Last Modified"),
    (DECKLIST_SORT_BY_NAME, "Deck Name"),
    (DECKLIST_SORT_BY_CARD_COUNT, "Card Count"),
]

# Decklist Pagination
DECKLIST_PAGE_SIZE = 30

SETS_IN_ORDER = [
    "PR",  # Promos
    "PR2015",
    "WL",
    "RL",
    "BE",
    "World",
    "World2015",
    "World2016",
    "World2017",
    "World2018",
    "World2019",
    "World2020",
    "World2021",
    "World2022",
    "World2023",
    "World2024",
    "World2025",
    "World2026",
    "World2027",
    "World2028",
    "WGP",
    "WPR",
    "WPR2015",
    "WPR2016",
    "WPR2017",
    "WPR2018",
    "WPR2019",
    "WPR2020",
    "WPR2021",
    "WPR2022",
    "WPR2023",
    "WPR2024",
    "WPR2025",
    "WPR2026",
    "WPR2027",
    "WPR2028",
    "BaB",
    "Pre",
    "Souvenir",
    "Judge",
    "BSR",  # Basic Rulers
    "CMF",
    "TAT",
    "MPR",
    "MOA",
    "VIN001",
    "VS01",
    "SKL",
    "TTW",
    "TMS",
    "BFA",
    "VIN002",
    "FOWMOVIE",
    "SDL1",
    "SDL2",
    "SDL3",
    "SDL4",
    "SDL5",
    "CFC",
    "L1 Buy a Box",
    "L1 Prerelease Party",
    "LEL",
    "L2 Buy a Box",
    "L2 Prerelease Party",
    "VIN003",
    "RDE",
    "L3 Buy a Box",
    "L3 Prerelease Party",
    "ENW",
    "L4 Buy a Box",
    "L4 Prerelease Party",
    "SDR1",
    "SDR2",
    "SDR3",
    "SDR4",
    "SDR5",
    "ACN",
    "R1 Buy a Box",
    "R1 Prerelease Party",
    "ADK",
    "R2 Buy a Box",
    "R2 Prerelease Party",
    "TSW",
    "R3 Buy a Box",
    "R3 Prerelease Party",
    "R3 Quest",
    "SDR6",
    "WOM",
    "R4 Buy a Box",
    "R4 Prerelease Party",
    "SDV1",
    "SDV2",
    "SDV3",
    "SDV4",
    "SDV5",
    "NDR",
    "V1 Buy a Box",
    "V1 Prerelease Party",
    "SNV",
    "V2 Buy a Box",
    "V2 Prerelease Party",
    "AOA V3 Buy 2",
    "AOA",
    "V3 Buy a Box",
    "V3 Buy 2 Boxes",
    "V3 Prerelease Party",
    "DBV",
    "V4 Buy a Box",
    "V4 Buy 2 Boxes",
    "V4 Prerelease Party",
    "SDAO1",
    "AO1 Buy a Box",
    "AO1 Buy a BoxJ",
    "AO1 Prerelease Party",
    "AO1",
    "SDAO2",
    "AO2 Buy a Box",
    "AO2 Buy a BoxJ",
    "AO2 Prerelease Party",
    "AO2",
    "GITS2045SD",
    "GITS2045",
    "SOUVENIR038",
    "SOUVENIR039",
    "AO3 Buy a Box",
    "AO3 Prerelease Party",
    "AO3",
    "AO4 Buy a Box",
    "PofA Prerelease Party",
    "PofA",
    "PofAMS",
    "EDL",
    "S1 Buy a Box",
    "S1 Prerelease Party",
    "MSW",
    "S2 Buy a Box",
    "S2 Prerelease Party",
    "ROL",
    "ADW",
    "S3 Buy a Box",
    "S3 Prerelease Party",
    "TST",
    "S4 Buy a Box",
    "S4 Prerelease Party",
    "DSD",
    "D1 Buy a Box",
    "D1 Prerelease Party",
    "GOG",
    "D2 Buy a Box",
    "D2 Prerelease Party",
    "GRL",
    "D3 Buy a Box",
    "D3 Prerelease Party",
    "GRV",
    "HSD",
    "NWE",
    "H1 Buy a Box",
    "H1 Prerelease Party",
    "TUS",
    "H2 Buy a Box",
    "H2 Prerelease Party",
    "TWS",
    "H3 Buy a Box",
    "H3 Prerelease Party",
    "CMB",
    "H4 Buy a Box",
    "H4 Prerelease Party",
    "ABC",
    "ABC-WB",
    "ABC-WD",
    "ABC-RG",
    "ABC-RD",
    "ABC-BG",
    "H5 Buy a Box",
    "H5 Prerelease Party",
    "CST",
    "MC02",  # Memoria Collection,
    "JRP",
    "H6 Buy a Box",
    "H6 Prerelease Party",
    "H6 Prerelease PartyJ",
    "MC03",
    "MP01",
    "TSD1",
    "TSD2",
    "TTT",
    "T1 Buy a Box",
    "T1 Prerelease Party",
    "MC04",
    "TSR",
    "T2 Buy a Box",
    "T2 Prerelease Party",
    "MC05",
    "ABC-SD01",
    "ABC-SD02",
    "ABC-SD03",
    "ABC-SD04",
    "ABC-SD05",
    "ABC-SD06",
    "ABC-SD07",
    "ABC-SD08",
    "ABC-SD09",
    "ABC-SD10",
    "ABC-SD11",
    "TEU",
    "T3 Buy a Box",
    "T3 Prerelease Party",
    "MC06",
    "MP02",
    "MC07",
    "TOP",
    "T4 Buy a Box",
    "T4 Prerelease Party",
    "MC08",
    "ESD1",
    "ESD2",
    "DRC",
    "DRC Prerelease Party",
    "DRC Buy a Box",
    "DRC Video",
    "MC09",
    "JRV",
    "JRV Prerelease Party",
    "JRV Buy a Box",
    "ATD",
    "MP03",
    "MC10",
]

SEARCH_CARD_TYPES_INCLUDE = {
    "Addition": [
        "Addition:Field",
        "Addition: Field",
        "Addition:Resonator",
        "Addition:J/Resonator",
        "Addition:Ruler/J-ruler",
    ],
    "Addition:Field": ["Addition: Field"],
    "Resonator": ["Resonator (Shift)", "Resonator (Stranger)"],
    "Chant": ["Spell:Chant", "Spell:Chant-Instant", "Spell:Chant-Standby"],
    "Regalia": ["Regalia (Shift)"],
    "Ruler": ["Basic Ruler"],
    "J-Ruler": ["Basic J-Ruler"],
    "Rune": ["Master Rune"],
}

SEARCH_SETS_INCLUDE = {
    "BFA": ["FOWMOVIE"],
    "WL": ["BE"],
    "BaB": [
        "L1 Buy a Box",
        "L2 Buy a Box",
        "L3 Buy a Box",
        "L4 Buy a Box",
        "R1 Buy a Box",
        "R2 Buy a Box",
        "R3 Buy a Box",
        "R4 Buy a Box",
        "V1 Buy a Box",
        "V2 Buy a Box",
        "AOA V3 Buy 2",
        "V3 Buy a Box",
        "V3 Buy 2 Boxes",
        "V4 Buy a Box",
        "V4 Buy 2 Boxes",
        "AO1 Buy a Box",
        "AO1 Buy a BoxJ",
        "AO2 Buy a Box",
        "AO2 Buy a BoxJ",
        "AO3 Buy a Box",
        "AO3 Buy a BoxJ",
        "AO4 Buy a Box",
        "AO4 Buy a BoxJ",
        "S1 Buy a Box",
        "S2 Buy a Box",
        "S3 Buy a Box",
        "S4 Buy a Box",
        "D1 Buy a Box",
        "D2 Buy a Box",
        "D3 Buy a Box",
        "H1 Buy a Box",
        "H2 Buy a Box",
        "H3 Buy a Box",
        "H4 Buy a Box",
        "H5 Buy a Box",
        "H6 Buy a Box",
        "MP01-ACV",
        "T1 Buy a Box",
        "T2 Buy a Box",
        "T3 Buy a Box",
        "MP02-BAB",
        "T4 Buy a Box",
        "JRV Buy a Box",
        "DRC Buy a Box",
    ],
    "Pre": [
        "L1 Prerelease Party",
        "L2 Prerelease Party",
        "L3 Prerelease Party",
        "L4 Prerelease Party",
        "R1 Prerelease Party",
        "R2 Prerelease Party",
        "R3 Prerelease Party",
        "R4 Prerelease Party",
        "V1 Prerelease Party",
        "V2 Prerelease Party",
        "V3 Prerelease Party",
        "V4 Prerelease Party",
        "AO1 Prerelease Party",
        "AO2 Prerelease Party",
        "AO3 Prerelease Party",
        "PofA Prerelease Party",
        "S1 Prerelease Party",
        "S2 Prerelease Party",
        "S3 Prerelease Party",
        "S4 Prerelease Party",
        "D1 Prerelease Party",
        "D2 Prerelease Party",
        "D3 Prerelease Party",
        "H1 Prerelease Party",
        "H2 Prerelease Party",
        "H3 Prerelease Party",
        "H4 Prerelease Party",
        "H5 Prerelease Party",
        "H6 Prerelease Party",
        "H6 Prerelease PartyJ",
        "T1 Prerelease Party",
        "T2 Prerelease Party",
        "T3 Prerelease Party",
        "T4 Prerelease Party",
        "JRV Prerelease Party",
        "DRC Prerelease Party",
    ],
    "World": [
        "World2015",
        "World2016",
        "World2017",
        "World2018",
        "World2019",
        "World2020",
        "World2021",
        "World2022",
        "World2023",
        "World2024",
        "World2025",
        "World2026",
        "World2027",
        "World2028",
    ],
    "WPR": [
        "WPR2015",
        "WPR2016",
        "WPR2017",
        "WPR2018",
        "WPR2019",
        "WPR2020",
        "WPR2021",
        "WPR2022",
        "WPR2023",
        "WPR2024",
        "WPR2025",
        "WPR2026",
        "WPR2027",
        "WPR2028",
    ],
    "CFC": [
        "L1 Prerelease Party",
        "L1 Buy a Box",
    ],
    "LEL": [
        "L2 Prerelease Party",
        "L2 Buy a Box",
    ],
    "RDE": [
        "L3 Prerelease Party",
        "L3 Buy a Box",
    ],
    "ENW": [
        "L4 Prerelease Party",
        "L4 Buy a Box",
    ],
    "ACN": [
        "R1 Prerelease Party",
        "R1 Buy a Box",
    ],
    "ADW": [
        "R2 Prerelease Party",
        "R2 Buy a Box",
    ],
    "TSW": [
        "R3 Prerelease Party",
        "R3 Buy a Box",
        "R3 Quest",
    ],
    "WOM": [
        "R4 Prerelease Party",
        "R4 Buy a Box",
    ],
    "NDR": [
        "V1 Prerelease Party",
        "V1 Buy a Box",
    ],
    "SVN": [
        "V2 Prerelease Party",
        "V2 Buy a Box",
    ],
    "AOA": [
        "V3 Prerelease Party",
        "V3 Buy a Box",
        "V3 Buy 2 Boxes",
        "AOA V3 Buy 2",
    ],
    "DBV": [
        "V4 Prerelease Party",
        "V4 Buy a Box",
        "V4 Buy 2 Boxes",
    ],
    "AO1": ["AO1 Buy a Box", "AO1 Buy a BoxJ", "AO1 Prerelease Party"],
    "AO2": ["AO2 Buy a Box", "AO2 Buy a BoxJ", "AO2 Prerelease Party"],
    "AO3": ["AO3 Buy a Box", "AO3 Buy a BoxJ", "AO3 Prerelease Party"],
    "PofA": ["AO4 Buy a Box", "AO4 Buy a BoxJ", "PofA Prerelease Party"],
    "EDL": [
        "S1 Buy a Box",
        "S1 Prerelease Party",
    ],
    "MSW": [
        "S2 Buy a Box",
        "S2 Prerelease Party",
    ],
    "ADW": [
        "S3 Buy a Box",
        "S3 Prerelease Party",
    ],
    "TST": [
        "S4 Buy a Box",
        "S4 Prerelease Party",
    ],
    "GOG": ["D1 Buy a Box", "D1 Prerelease Party"],
    "GRL": ["D2 Buy a Box", "D2 Prerelease Party"],
    "GRV": ["D3 Prerelease Party", "D3 Buy a Box"],
    "NWE": ["H1 Buy a Box", "H1 Prerelease Party"],
    "TUS": ["H2 Buy a Box", "H2 Prerelease Party"],
    "TWS": ["H3 Buy a Box", "H3 Prerelease Party"],
    "CMB": ["H4 Prerelease Party", "H4 Buy a Box"],
    "CST": ["H5 Buy a Box", "H5 Prerelease Party", "MC02"],
    "JRP": [
        "H6 Buy a Box",
        "H6 Prerelease Party",
        "H6 Prerelease PartyJ",
        "MC03",
    ],
    "TTT": ["T1 Buy a Box", "MC04", "T1 Prerelease Party"],
    "TSR": ["T2 Buy a Box", "MC05", "T2 Prerelease Party"],
    "TEU": ["T3 Buy a Box", "MC06", "T3 Prerelease Party"],
    "MP02": [
        "MC07",
    ],
    "TOP": ["T4 Buy a Box", "MC08", "T4 Prerelease Party"],
    "DRC": [
        "E1 Buy a Box",
        "MC09",
        "E1 Prerelease Party",
        "DRC Buy a Box",
        "DRC Prerelease Party",
        "DRC Video",
        "MC09",
    ],
    "JRV": ["JRV Buy a Box", "JRV Prerelease Party"],
    "MP03": [
        "MC10",
    ],
}

KEYWORDS_CHOICES = [
    ("[Tales]", "Tales"),
    ("[Villains]", "Villains"),
    ("[Precision]", "Precision"),
    ("[Flying]", "Flying"),
    ("[Explode]", "Explode"),
    ("[First Strike]", "First Strike"),
    ("[Swiftness]", "Swiftness"),
    ("[Imperishable]", "Imperishable"),
    ("[Quickcast]", "Quickcast"),
    ("[Remnant]", "Remnant"),
    ("[Barrier]", "Barrier"),
    ("[Will of Despair]", "Will of Despair"),
    ("[Will of Hope]", "Will of Hope"),
    ("[Seal]", "Seal"),
    ("[Drain]", "Drain"),
    ("[Null]", "Null"),
    ("[Drain]", "Drain"),
    ("[Bloodlust]", "Bloodlust"),
    ("[Pierce]", "Pierce"),
    ("[Barrier]", "Barrier"),
    ("[Divinity]", "Divinity"),
    ("[Bane]", "Bane"),
    ("[Rune]", "Rune"),
    ("[Mythic]", "Mythic"),
    ("[Eternal]", "Eternal"),
    ("[Limit Break]", "Limit Break"),
    ("[Revenge]", "Revenge"),
    ("[Fallen]", "Fallen"),
    ("[Revolution]", "Revolution"),
    ("[Awakening]", "Awakening"),
    ("[Incarnation]", "Incarnation"),
    ("God's Art", "God's Art"),
    ("[Trigger]", "Trigger"),
    ("[Stealth]", "Stealth"),
    ("[Evolution]", "Evolution"),
    ("[Shift]", "Shift"),
    ("[Limit]", "Limit"),
    ("[Energize]", "Energize"),
    ("[Bestow]", "Bestow"),
    ("[Mana]", "Mana"),
    ("[Torrent]", "Torrent"),
    ("[Judgment]", "Judgment"),
    ("[Inheritance]", "Inheritance"),
    ("[Resonance]", "Resonance"),
    ("[Mobilize]", "Mobilize"),
    ("Sealed Item", "Sealed Item"),
    ("[Crest]", "Crest"),
    ("[Grimoire]", "Grimoire"),
    ("[Legend]", "Legend"),
    ("[Enter]", "Enter"),
    ("[Faith]", "Faith"),
    ("[Stranger]", "Stranger"),
    ("[Target Attack]", "Target Attack"),
    ("[Dive]", "Dive"),
    ("[Tag]", "Tag"),
    ("[Guidance]", "Guidance"),
    ("[Revolution Order]", "Revolution Order"),
    ("[Revolution]", "Revolution"),
    ("[Force Command]", "Force Command"),
    ("[Force Resonance]", "Force Resonance"),
    ("[Dragon Emblem]", "Dragon Emblem"),
    ("[Force]", "Force"),
    ("[Union Seven <Machine>]", "Union Seven <Machine>"),
    ("[Union Seven <New Twelve Olympian Gods>]", "Union Seven <New Twelve Olympian Gods>"),
    ("[Convoke]", "Convoke"),
]


ZONES_SHOWN_BY_DEFAULT = ["Ruler Area", "Main Deck", "Magic Stone Deck", "Side Deck"]

SITE_ICON_URL = static("img/wind.png")

FORMATS = ["Wanderer"]

BANNED_CARDS = [
    {
        "format_name": "Wanderer",
        "cards": [
            "EDL-064",
            "TST-063",
            "GOG-031",
            "TTW-006",
            "TMS-094",
            "TTW-099",
            "TST-024",
            "CFC-037",  # Hook is also BAB promo but not in the DB
            "ENW-049",
            "ENW-051",
            "MSW-053",
            "SDV4-005",
            "DBV-062",  # Reprint of SDV4-005
            "CMF-069",
            "CMF-071",
            "VIN001-054",  # Reprint of CMF-071
            "EDL-062",
            "ADK-106",
            "ENW-063",
            "TSW-109",
            "TSW-109J",
            "ADK-113",
            "TMS-064",  # Also WL005 promo (wall of wind)
            "ENW-074",
            "DBV-079",
            "AOA-100",
            "DBV-092",
            "TST-075",
            "DBV-095",
            "AO3-082",
            "MSW-102",
        ],
        "combination_bans": [
            ["TAT-090", "GRV-085"],
            ["TTW-064", "ROL-017"],
            ["TTW-097", "GRL-006"],
            ["TSW-094", "GRV-082"],
            ["TSW-149", "GRV-026"],
            ["ACN-096", "GRL-034"],
            ["AO3-046", "PofA-111"],
            ["EDL-076", "EDL-096"],
            ["EDL-074", "ROL-018"],
            ["MSW-002", "MSW-042"],
            ["MSW-026", "MSW-073"],
            ["MSW-042", "MSW-026"],
            ["ROL-013", "ADW-030"],
            ["ADW-003", "ADW-026"],
            ["ADW-016", "ADW-020"],
            ["TST-067", "TST-073"],
            ["TST-078", "GRV-060"],
            ["DSD-006", "DSD-008"],
            ["GOG-023", "GOG-024"],
            ["GOG-050", "GOG-078"],
            ["GRL-067", "GRL-083"],
            ["GRL-030", "GRL-038"],
            ["GRV-051", "GRV-070"],
            ["GRV-064", "GRV-085"],
        ],
    }
]

PICK_PERIOD_ALL_TIME = 0
PICK_PERIOD_SEVEN_DAYS = 7
PICK_PERIOD_THIRTY_DAYS = 30
PICK_PERIOD_NINETY_DAYS = 90


PICK_PERIOD_DAYS = [  # Also includes "all time" when created in importMetricPeriods
    PICK_PERIOD_SEVEN_DAYS,
    PICK_PERIOD_THIRTY_DAYS,
    PICK_PERIOD_NINETY_DAYS,
]

PICK_PERIOD_CHOICES = [
    (str(PICK_PERIOD_ALL_TIME), "All Time"),
    (str(PICK_PERIOD_SEVEN_DAYS), "7 Days"),
    (str(PICK_PERIOD_THIRTY_DAYS), "30 Days"),
    (str(PICK_PERIOD_NINETY_DAYS), "90 Days"),
]

PACK_OPENING_SETS = [
    "cmf",
    "tat",
    "mpr",
    "moa",
    "skl",
    "ttw",
    "tms",
    "bfa",
    "cfc",
    "lel",
    "rde",
    "enw",
    "acn",
    "adk",
    "tsw",
    "wom",
    "ndr",
    "snv",
    "aoa",
    "dbv",
    "ao1",
    "ao2",
    "gits2045",
    "ao3",
    "pofa",
    "edl",
    "msw",
    "rol",
    "adw",
    "tst",
    "gog",
    "grl",
    "grv",
    "nwe",
    "tus",
    "tws",
    "cmb",
    "cst",
    "jrp",
    "mp01",
]

MODE_PRIVATE = "private"
MODE_TOURNAMENT = "tournament"

DECK_LIST_SHARE_MODE_CHOICES = [[MODE_PRIVATE, MODE_PRIVATE], [MODE_TOURNAMENT, MODE_TOURNAMENT]]

DECK_LIST_LOCK_MODE_CHOICES = [[MODE_PRIVATE, MODE_PRIVATE], [MODE_TOURNAMENT, MODE_TOURNAMENT]]

PLAYER_REGISTRATION_REQUESTED = "requested"
PLAYER_REGISTRATION_ACCEPTED = "accepted"
PLAYER_REGISTRATION_COMPLETED = "completed"

TOURNAMENT_PLAYER_REGISTRATION_STATES = [
    [PLAYER_REGISTRATION_REQUESTED, PLAYER_REGISTRATION_REQUESTED],
    [PLAYER_REGISTRATION_ACCEPTED, PLAYER_REGISTRATION_ACCEPTED],
    [PLAYER_REGISTRATION_COMPLETED, PLAYER_REGISTRATION_COMPLETED],
]

TOURNAMENT_PHASE_CREATED = "created"
TOURNAMENT_PHASE_REGISTRATION = "registration"
TOURNAMENT_PHASE_SWISS = "swiss"
TOURNAMENT_PHASE_TOPS = "tops"
TOURNAMENT_PHASE_COMPLETED = "completed"

TOURNAMENT_PHASES = [
    [TOURNAMENT_PHASE_CREATED, TOURNAMENT_PHASE_CREATED],
    [TOURNAMENT_PHASE_REGISTRATION, TOURNAMENT_PHASE_REGISTRATION],
    [TOURNAMENT_PHASE_SWISS, TOURNAMENT_PHASE_SWISS],
    [TOURNAMENT_PHASE_TOPS, TOURNAMENT_PHASE_TOPS],
    [TOURNAMENT_PHASE_COMPLETED, TOURNAMENT_PHASE_COMPLETED],
]


TOURNAMENT_PLAYER_REGISTRATION_STATES = [
    [PLAYER_REGISTRATION_REQUESTED, PLAYER_REGISTRATION_REQUESTED],
    [PLAYER_REGISTRATION_ACCEPTED, PLAYER_REGISTRATION_ACCEPTED],
    [PLAYER_REGISTRATION_COMPLETED, PLAYER_REGISTRATION_COMPLETED],
]


DECK_TYPE_WANDERER = "Wanderer"
DECK_TYPE_ABC = "ABC"
DECK_TYPE_CUSTOM = "Custom"

DECK_TYPE_VALUES = [DECK_TYPE_WANDERER, DECK_TYPE_ABC, DECK_TYPE_CUSTOM]

DECK_TYPE_CHOICES = [
    [DECK_TYPE_WANDERER, DECK_TYPE_WANDERER],
    [DECK_TYPE_ABC, DECK_TYPE_ABC],
    [DECK_TYPE_CUSTOM, DECK_TYPE_CUSTOM],
]

SOLO_MODE_STYLE = "solo-mode"

PARADOX_FORMAT = "Paradox"

WANDERER_FORMAT = "Wanderer"
