from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from .CardType import Card, CardColour, CardArtist
from .User import Profile
from .DeckList import DeckListCard, DeckListZone, DeckList
from .Spoilers import SpoilerSeason
from .Banlist import CombinationBannedCards, BannedCard, Format
from .Rulings import Ruling
from .Metrics import PickPeriod, MostPickedCardPickRate, AttributePickRate, CardTypePickRate, CardTotalCostPickRate
from .Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
'''
# iterate through the modules in the current package
package_dir = Path(__file__).resolve().parent
for (_, module_name, _) in iter_modules([package_dir]):

    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute):
            # Add the class to this package's variables
            globals()[attribute_name] = attribute
'''
