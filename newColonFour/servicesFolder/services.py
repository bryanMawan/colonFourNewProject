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
import re
from django.utils.html import escape
import redis
from django.conf import settings
from .country_choices import COUNTRY_CHOICES

logger = logging.getLogger(__name__)
geo_db = GeolocationDatabase()
default_query = "3 Rue de l'Est, 75020 Paris, France"

default_image = '/static/images/photoDefault.jpg'
dancer_success_msg = " has been added as a dancer. Create more dancers or proceed by clicking the 'Next' button or "

EVENT_AJAX_CACHE_KEY = ""






BATTLE_TYPE_CHOICES = [
        ('1vs1', '1vs1'),
        ('2vs2', '2vs2'),
        ('3vs3', '3vs3'),
        ('crew', 'Crew'),
        # Add more battle types if needed
    ]

LEVEL_CHOICES = [
        ('Open', 'Open'),
        ('Rookie', 'Rookie'),
        ('Advanced', 'Advanced'),
        # Add more battle types if needed
    ]


def generate_cache_key(self, key_string):
        """
        Generate an MD5 hash for the provided key string to be used as a cache key.
        
        Args:
            key_string (str): The input string to be hashed.
        
        Returns:
            str: The resulting MD5 hash as a hexadecimal string.
        """
        return hashlib.md5(key_string.encode()).hexdigest()


def generate_unique_slug(model, value, slug_field="slug"):
    slug = slugify(value) or get_random_string(8)
    original_slug = slug
    counter = 1

    while model.objects.filter(**{slug_field: slug}).exists():
        slug = f"{original_slug}-{counter}"
        counter += 1

    return slug

def sanitize_instagram_account(instagram_account):
    if instagram_account:
        instagram_account = escape(instagram_account)
        if not re.match(r'^[\w\.\-]+$', instagram_account):
            return None, 'Invalid Instagram account.'
    return instagram_account, None

# gpt: update this method to take the instagram account value as args and update in the organizer profiles instagram_account field as well
def update_organizer_profile(user, gdpr_consented, instagram_account):
    OrganizerProfile = apps.get_model('newColonFour', 'OrganizerProfile')

    OrganizerProfile.objects.update_or_create(
        user=user, 
        defaults={
            'gdpr_consented': gdpr_consented,
            'instagram_account': instagram_account
        }
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

    # Proceed with distance calculation using the default coordinates
    # Calculate the distance
    distance = haversine(lat1, lon1, lat2, lon2)

    # Log the calculated distance and city names for debugging
    logger.debug(f"Distance: {city1} to {city2} - {distance:.2f} kilometers")

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

    # Check if the submitted code matches the expected code
    if submitted_code == expected_code:
        return True
    else:
        return False
    
def send_code(code, number):
    print(f"{code} for {number}")

def hash_telephone_number(telephone_number):
    # Ensure the input is a string and encode it
    encoded_number = str(telephone_number).encode()
    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()
    # Update the hash object with the encoded telephone number
    hash_object.update(encoded_number)
    # Return the hexadecimal representation of the digest
    return hash_object.hexdigest()




def get_redis_client():
    """Get a Redis client using Django settings and print the LOCATION."""
    location = settings.CACHES['default']['LOCATION']
    
    # Print the LOCATION to understand its format
    print(f"Redis LOCATION: {location}")
    
    # Extract the host and port from the LOCATION string
    if location.startswith('redis://'):
        # Remove the 'redis://' part and split the rest
        parts = location[7:].split(':')
        
        try:
            host = parts[0]
            port_and_db = parts[1].split('/')
            port = int(port_and_db[0])
            db = int(port_and_db[1]) if len(port_and_db) > 1 else 0  # Default to db 0 if not specified
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to parse Redis location: {location}") from e
    else:
        raise ValueError(f"Unexpected Redis LOCATION format: {location}")

    return redis.Redis(
        host=host,
        port=port,
        db=db
    )
    
def delete_keys_with_prefix(prefix):
    # Get the Redis client
    redis_conn = get_redis_client()
    
    # Initialize cursor and pattern
    cursor = 0
    pattern = f"{prefix}*"
    
    while True:
        # Use the SCAN command to iterate over keys
        cursor, keys = redis_conn.scan(cursor, match=pattern)
        
        if keys:
            # Delete each key
            for key in keys:
                redis_conn.delete(key)
                print(f"Deleted key: {key.decode('utf-8')}")
        
        # Break the loop if the cursor is zero (no more keys to scan)
        if cursor == 0:
            break
