from django.contrib import admin
from django.apps import apps

# Register your models here.
for model_name, model in apps.get_app_config('cardDatabase').models.items():
    admin.site.register(model)