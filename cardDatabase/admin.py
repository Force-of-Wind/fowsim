from django.contrib import admin
from cardDatabase.models.Ability import *
from cardDatabase.models.CardType import *
from cardDatabase.models.Effects import OneTimeEffect
from cardDatabase.models.User import Profile
from cardDatabase.models.DeckList import DeckList, DeckListCard, DeckListZone, UserDeckListZone
from cardDatabase.models.Spoilers import SpoilerSeason
from cardDatabase.models.Banlist import CombinationBannedCards, BannedCard, Format
from cardDatabase.models.Rulings import Ruling, Restriction, RestrictionAction, RestrictionException, ExceptionAction
from cardDatabase.models.Metrics import *

class AbilityTextInline(admin.TabularInline):
    model = CardAbility
    extra = 1


class CardsWithAbilityTextInline(admin.TabularInline):
    model = CardAbility


class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'card_id', )
    search_fields = ['name', 'name_without_punctuation', 'ability_texts__text', 'card_id']
    inlines = [AbilityTextInline]
    autocomplete_fields = ['races', 'artists']

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


class BannedCardAdmin(admin.ModelAdmin):
    search_fields = ['card__name', 'card__name_withoout_punctuation']
    autocomplete_fields = ['card']



class CombinationBannedCardsAdmin(admin.ModelAdmin):
    search_fields = ['cards__name', 'cards__name_without_punctuation', 'cards']
    autocomplete_fields = ['cards']


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


class RaceAdmin(admin.ModelAdmin):
    search_fields = ['name']

class ArtistAdmin(admin.ModelAdmin):
    search_fields = ['name']

class SetAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code']

class FormatAdmin(admin.ModelAdmin):
    autocomplete_fields = ['sets']
    search_fields = ['sets__name', 'sets__code', 'sets']


admin.site.register(OneTimeEffect)
admin.site.register(Card, CardAdmin)
admin.site.register(Tag)
admin.site.register(Set, SetAdmin)
admin.site.register(Cluster)
admin.site.register(AbilityText, AbilityTextAdmin)
admin.site.register(AbilityStyle)
admin.site.register(Profile)
admin.site.register(Keyword)
admin.site.register(DeckList)
admin.site.register(DeckListCard)
admin.site.register(DeckListZone)
admin.site.register(UserDeckListZone)
admin.site.register(SpoilerSeason)
admin.site.register(BannedCard, BannedCardAdmin)
admin.site.register(Format, FormatAdmin)
admin.site.register(CombinationBannedCards, CombinationBannedCardsAdmin)
admin.site.register(Ruling, RulingAdmin)
admin.site.register(Restriction)
admin.site.register(RestrictionAction)
admin.site.register(RestrictionException)
admin.site.register(ExceptionAction)
admin.site.register(Race, RaceAdmin)
admin.site.register(CardColour)
admin.site.register(MostPickedCardPickRate)
admin.site.register(CardTotalCostPickRate)
admin.site.register(CardTypePickRate)
admin.site.register(AttributePickRate)
admin.site.register(PickPeriod)
admin.site.register(Type)
admin.site.register(CardArtist, ArtistAdmin)