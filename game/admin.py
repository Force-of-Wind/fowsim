import inspect
import sys

from django.contrib import admin
from django.apps import apps

from .models.Deck import DeckType

class DeckTypeAdmin(admin.ModelAdmin):
        list_display = ('name',)


admin.site.register(DeckType, DeckTypeAdmin)

# Register your models here.
for model_name, model in apps.get_app_config('game').models.items():
        #  Don't register a class twice, manually register overriden admins
        if model not in [DeckType]:
                admin.site.register(model)
