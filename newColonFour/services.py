# services.py

from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

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

def get_all_styles():
    # Dynamically fetch models
    Dancer = apps.get_model('newColonFour', 'Dancer')
    Event = apps.get_model('newColonFour', 'Event')
    
    all_styles = set()

    # Check if there are any Event instances
    if Event.objects.exists():
        # Get styles from Events
        for event in Event.objects.all():
            all_styles.update(event.get_styles())
    else:
        # If no Event instances, get styles from Dancers
        for dancer in Dancer.objects.all():
            all_styles.update(dancer.special_get_styles())

    return list(all_styles)


def set_battle_organizer(battle, user):
    OrganizerProfile = apps.get_model('newColonFour', 'OrganizerProfile')
    organizer_profile, created = OrganizerProfile.objects.get_or_create(user=user)
    if created:
        logger.info(f"Created new OrganizerProfile for user {user}")
    else:
        logger.info(f"Found existing OrganizerProfile for user {user}")

    battle.organizer = organizer_profile
    return battle

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