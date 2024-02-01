# services.py

from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.apps import apps

default_image = '/static/images/photoDefault.jpg'
dancer_success_msg = " has been added as a dancer. Create more dancers or proceed by clicking the 'Next' button or "

COUNTRY_CHOICES = [
    ('USA', 'United States'),
    ('CAN', 'Canada'),
    # Add more countries as needed
]

BATTLE_TYPE_CHOICES = [
        ('1vs1', '1vs1'),
        ('2vs2', '2vs2'),
        ('3vs3', '3vs3'),
        ('crew', 'Crew'),
        # Add more battle types if needed
    ]

LEVEL_CHOICES = [
        ('Open', 'Open'),
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        # Add more battle types if needed
    ]


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

def get_user_or_client_ip(request):
    if request.user.is_authenticated:
        return request.user
    else:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip