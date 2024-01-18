# services.py

from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.apps import apps

default_image = '/static/images/photoDefault.jpg'


def generate_unique_slug(model, value, slug_field="slug"):
    slug = slugify(value) or get_random_string(8)
    original_slug = slug
    counter = 1

    while model.objects.filter(**{slug_field: slug}).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug

def update_organizer_profile(user, gdpr_consented):
    OrganizerProfile = apps.get_model('newColonFour', 'OrganizerProfile')

    OrganizerProfile.objects.update_or_create(
        user=user, 
        defaults={'gdpr_consented': gdpr_consented}
    )

