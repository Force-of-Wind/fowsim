from django.contrib import admin
from cardDatabase.models.Ability import *
from cardDatabase.models.CardType import *
from cardDatabase.models.Effects import OneTimeEffect
from cardDatabase.models.User import Profile


class AbilityTextInline(admin.TabularInline):
    model = AbilityText.cards.through


class CardsWithAbilityTextInline(admin.TabularInline):
    model = Card.ability_texts.through


class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'card_id', )
    search_fields = ['name', 'ability_texts__text', 'card_id']
    inlines = [AbilityTextInline]

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.exclude = ('ability_texts',)
        return super().get_form(request, obj=obj, **kwargs)


class AbilityTextAdmin(admin.ModelAdmin):
    list_display = ('text',)
    inlines = [CardsWithAbilityTextInline]
    search_fields = ['text']


admin.site.register(OneTimeEffect)
admin.site.register(Card, CardAdmin)
admin.site.register(AbilityText, AbilityTextAdmin)
admin.site.register(Profile)
admin.site.register(Keyword)