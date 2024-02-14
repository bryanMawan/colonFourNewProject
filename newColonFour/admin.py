from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

app = apps.get_app_config('newColonFour')

for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        # This model is already registered
        pass

