from django.contrib import admin
from cardDatabase.models.Ability import *
from cardDatabase.models.CardType import *
from cardDatabase.models.Effects import OneTimeEffect
from cardDatabase.models.User import Profile
from cardDatabase.models.DeckList import DeckList, DeckListCard, DeckListZone, UserDeckListZone
from cardDatabase.models.Spoilers import SpoilerSeason
from cardDatabase.models.Banlist import CombinationBannedCards, BannedCard, Format
from cardDatabase.models.Rulings import Ruling


class AbilityTextInline(admin.TabularInline):
    model = CardAbility
    extra = 1


class CardsWithAbilityTextInline(admin.TabularInline):
    model = CardAbility


class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'card_id', )
    search_fields = ['name', 'ability_texts__text', 'card_id']
    inlines = [AbilityTextInline]

    class Media:
        css = {
            'all': ('css/admin/card_admin_fixes.css',)
        }

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.exclude = ('ability_texts',)
        return super().get_form(request, obj=obj, **kwargs)


class AbilityTextAdmin(admin.ModelAdmin):
    list_display = ('text',)
    inlines = [CardsWithAbilityTextInline]
    search_fields = ['text']


class CombinationBannedCardsInline(admin.TabularInline):
    model = CombinationBannedCards.cards.through


class CombinationBannedCardsAdmin(admin.ModelAdmin):
    exclude = ('cards',)
    inlines = [
        CombinationBannedCardsInline,
    ]


class RulingAdmin(admin.ModelAdmin):
    search_fields = ['card__name', 'card__name_without_punctuation', 'text']
    fields = ['card', 'text', 'company_confirmed']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.added_by = request.user.profile
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'card':
            kwargs['queryset'] = Card.objects.all().order_by('name')
        return super(RulingAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(OneTimeEffect)
admin.site.register(Card, CardAdmin)
admin.site.register(AbilityText, AbilityTextAdmin)
admin.site.register(Profile)
admin.site.register(Keyword)
admin.site.register(DeckList)
admin.site.register(DeckListCard)
admin.site.register(DeckListZone)
admin.site.register(UserDeckListZone)
admin.site.register(SpoilerSeason)
admin.site.register(BannedCard)
admin.site.register(Format)
admin.site.register(CombinationBannedCards, CombinationBannedCardsAdmin)
admin.site.register(Ruling, RulingAdmin)
admin.site.register(Race)
admin.site.register(CardColour)
