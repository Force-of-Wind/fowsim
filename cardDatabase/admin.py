from django.contrib import admin
from cardDatabase.models.Ability import *
from cardDatabase.models.CardType import *
from cardDatabase.models.Effects import OneTimeEffect

class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'card_id', )
    search_fields = ['name', 'ability_texts__text']

class AbilityTextAdmin(admin.ModelAdmin):
    list_display = ('text',)

admin.site.register(OneTimeEffect)
admin.site.register(Card, CardAdmin)
admin.site.register(AbilityText, AbilityTextAdmin)