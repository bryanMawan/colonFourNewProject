# services.py
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string
from django.apps import apps
import math
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware, utc
from django.core.exceptions import ValidationError
import logging
from .GeolocationDatabase import GeolocationDatabase
import pyotp
import hashlib
import base64
import time  # Import the time module

logger = logging.getLogger(__name__)
geo_db = GeolocationDatabase()
default_query = "3 Rue de l'Est, 75020 Paris, France"

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
    
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

def distance_between_cities(city1, city2):
    """
    Calculate the distance between two cities using their names. If the location lookup fails,
    use default coordinates (for Paris, France) provided by the GeolocationDatabase.

    :param city1: The name of the first city.
    :param city2: The name of the second city.
    :return: The distance in kilometers between the two cities, or None if both lookups fail.
    """
    lat1, lon1, success1 = geo_db.get_location(city1)
    lat2, lon2, success2 = geo_db.get_location(city2)

    
    # If either lookup fails, fall back to default coordinates for comparison
    if not success1:
        logger.warning(f"Lookup for city {city1} failed, using default coordinates.")
        lat1, lon1 = geo_db.default_lat, geo_db.default_lon
    
    if not success2:
        logger.warning(f"Lookup for city {city2} failed, using default coordinates.")
        lat2, lon2 = geo_db.default_lat, geo_db.default_lon

    # Proceed with distance calculation using either the looked-up or default coordinates
        # Calculate the distance
    distance = haversine(lat1, lon1, lat2, lon2)

    # Log the calculated distance and city names for debugging
    logger.debug(f"Distance between {city1} and {city2}: {distance} kilometers.")

    return distance
    
def sanitize_utc(utc_date_str):
    """
    Takes a UTC date string, validates, sanitizes it, and returns a timezone-aware datetime object.
    Returns None if the input is invalid.
    """
    try:
        utc_date = parse_datetime(utc_date_str)
        if utc_date and not is_aware(utc_date):
            utc_date = make_aware(utc_date, timezone=utc)
        return utc_date
    except (ValueError, OverflowError, ValidationError):
        # Return None or raise an error for invalid input
        return None

def update_event_location_point(battle, geo_db=geo_db):
    # No need to fetch the Battle instance, as it's already passed in
    # Assuming 'battle.location' exists and is similar in format to 'event.location'
    city = ", ".join(battle.location.split(",")[-2:])  # Get the last two items as the city

    lat, lon, success = geo_db.get_location(city)
    if success:
        # Set the battle's location_point field as a string (e.g., "40.7127281, -74.0060152")
        battle.location_point = f"{lat}, {lon}"
        battle.save()
    else:
        # Handle cases where location cannot be determined
        logger.warning(f"Location lookup failed for battle {battle.name} at {battle.location}")

def generate_totp_code(phone_number, interval=300):
    """
    Generates a time-based one-time password (TOTP) code based on a phone number.

    :param phone_number: The user's phone number as a unique identifier.
    :param interval: The time interval in seconds for the TOTP algorithm. Default is 30 seconds.
    :return: A 6-digit TOTP code as a string.
    """
    # Hash the phone number to use as a base for the secret key
    hash_digest = hashlib.sha256(phone_number.encode()).digest()
    
    # Base32 encode the hash digest to use as the TOTP secret key
    secret_key = base64.b32encode(hash_digest).decode('utf-8')

    # Create a TOTP object with the secret key
    totp = pyotp.TOTP(secret_key, interval=interval)

    # Generate a TOTP code
    totp_code = totp.now()

    return totp_code

def verify_totp_code(submitted_code, phone_number, interval=300):
    """
    Verifies a submitted TOTP code against the expected code generated with the user's phone number.

    :param submitted_code: The TOTP code submitted by the user.
    :param phone_number: The user's phone number used to generate the original TOTP code.
    :param interval: The time interval in seconds for the TOTP algorithm. Default is 30 seconds.
    :return: True if the code is correct and still valid, False otherwise.
    """
    # Generate the expected TOTP code using the same method as before
    expected_code = generate_totp_code(phone_number, interval=interval)
    print(expected_code)

    # Check if the submitted code matches the expected code
    if submitted_code == expected_code:
        return True
    else:
        return False
    
def send_code(code, number):
    print(f"{code} for {number}")
