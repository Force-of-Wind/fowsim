from django.contrib import admin
from cardDatabase.models.Ability import *
from cardDatabase.models.CardType import *
from cardDatabase.models.Effects import OneTimeEffect


admin.site.register(OneTimeEffect)