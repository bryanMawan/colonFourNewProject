from decouple import config
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeopyError
import logging
from django.core.cache import cache
import hashlib



# Configure logging to only log errors
logger = logging.getLogger(__name__)


class GeolocationDatabase:
    def __init__(self):
        self.connection_params = {
            "dbname": config('TEST_DB_NAME'),
            "user": config('TEST_DB_USER'),
            "password": config('TEST_DB_PASSWORD'),
            "host": config('TEST_DB_HOST'),
            "port": config('TEST_DB_PORT', default="5432"),
        }
        # Initialize database and geocoder
        self.init_db()
        self.geolocator = Nominatim(user_agent="your_user_agent_here")  # Adjust your user agent
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self.default_lat, self.default_lon = self.getDefaultCoordinates()

    def init_db(self):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    # Create table with index on city column
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS locations (
                            city TEXT PRIMARY KEY,
                            latitude REAL,
                            longitude REAL
                        )
                    ''')
                    # Create index for faster lookups
                    cursor.execute('CREATE INDEX IF NOT EXISTS idx_city ON locations (LOWER(city));')
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error during initialization: {e}")

    def generate_cache_key(self, key_string):
        """
        Generate an MD5 hash for the provided key string to be used as a cache key.
        
        Args:
            key_string (str): The input string to be hashed.
        
        Returns:
            str: The resulting MD5 hash as a hexadecimal string.
        """
        return hashlib.md5(key_string.encode()).hexdigest()

    def getDefaultCoordinates(self):
        city = "Paris, France"
        cache_key = self.generate_cache_key(city)
        cached_coords = cache.get(cache_key)
        
        if cached_coords:
            return cached_coords
        
        default_lat, default_lon = None, None
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(sql.SQL('SELECT latitude, longitude FROM locations WHERE LOWER(city) = LOWER(%s)'), (city,))
                    result = cursor.fetchone()
                    if result:
                        default_lat, default_lon = result['latitude'], result['longitude']
                    else:
                        location = self.geocode(city)
                        if location:
                            default_lat, default_lon = location.latitude, location.longitude
                            self.add_location(city, default_lat, default_lon)
            cache.set(cache_key, (default_lat, default_lon), timeout=60*60*2)  # Cache for 2 hours
        except (psycopg2.DatabaseError, GeopyError) as e:
            logger.error(f"Error ensuring default coordinates: {e}")
        
        return default_lat, default_lon


    def add_location(self, city, lat, lon):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    # Check if location already exists
                    cursor.execute(sql.SQL('SELECT 1 FROM locations WHERE LOWER(city) = LOWER(%s)'), (city,))
                    if not cursor.fetchone():
                        # Insert new location
                        cursor.execute(sql.SQL('INSERT INTO locations (city, latitude, longitude) VALUES (%s, %s, %s)'), (city, lat, lon))
                        conn.commit()
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error during insert: {e}")

    def get_location(self, city_country):
        cache_key = self.generate_cache_key(city_country)
        cached_coords = cache.get(cache_key)
        
        if cached_coords:
            return cached_coords + (True,)
        
        try:
            city = city_country
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(sql.SQL('SELECT latitude, longitude FROM locations WHERE LOWER(city) = LOWER(%s)'), (city,))
                    result = cursor.fetchone()
                    if result:
                        lat, lon = result['latitude'], result['longitude']
                        cache.set(cache_key, (lat, lon), timeout=60*60*2)  # Cache for 2 hours
                        return lat, lon, True
                    else:
                        location = self.geocode(city_country)
                        if location:
                            lat, lon = location.latitude, location.longitude
                            self.add_location(city, lat, lon)
                            cache.set(cache_key, (lat, lon), timeout=60*60*2)  # Cache for 2 hours
                            return lat, lon, True
                        else:
                            default_lat, default_lon = self.getDefaultCoordinates()
                            return default_lat, default_lon, False
        except (psycopg2.DatabaseError, GeopyError) as e:
            logger.error(f"Geocoding error: {e}")
            default_lat, default_lon = self.getDefaultCoordinates()
            return default_lat, default_lon, False

