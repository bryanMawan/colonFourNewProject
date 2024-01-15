# services.py

from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.apps import apps


def generate_unique_slug(model, value, slug_field="slug"):
    slug = slugify(value) or get_random_string(8)
    original_slug = slug
    counter = 1

    while model.objects.filter(**{slug_field: slug}).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug

def connectprofile(user, gdpr_consented=False):
    OrganizerProfile = apps.get_model('newColonFour', 'OrganizerProfile')
    
    organizer_profile, created = OrganizerProfile.objects.get_or_create(
        user=user, 
        defaults={'gdpr_consented': gdpr_consented}
    )

    if not created and gdpr_consented != organizer_profile.gdpr_consented:
        organizer_profile.gdpr_consented = gdpr_consented
        organizer_profile.save()