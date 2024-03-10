from decouple import config
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeopyError
import logging

logger = logging.getLogger(__name__)


class GeolocationDatabase:
    def __init__(self):
        self.connection_params = {
            "dbname": config('POSTGRES_DATABASE'),
            "user": config('POSTGRES_USER'),
            "password": config('POSTGRES_PASSWORD'),
            "host": config('POSTGRES_HOST'),
            # If you're using a non-default port, add it here
            "port": "5432"  # Or use config('POSTGRES_PORT') if your port is in the .env
        }
        self.init_db()
        self.geolocator = Nominatim(user_agent="your_user_agent_here")  # Adjust your user agent
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        self.default_lat, self.default_lon = self.getDefaultCoordinates()

    def init_db(self):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS locations (
                            city TEXT PRIMARY KEY,
                            latitude REAL,
                            longitude REAL
                        )
                    ''')
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error: {e}")

    def getDefaultCoordinates(self):
        city = "Paris, France"
        default_lat, default_lon = None, None
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(sql.SQL('SELECT latitude, longitude FROM locations WHERE city = %s'), (city,))
                    result = cursor.fetchone()
                    if result:
                        default_lat, default_lon = result['latitude'], result['longitude']
                    else:
                        location = self.geocode(city)
                        if location:
                            default_lat, default_lon = location.latitude, location.longitude
                            self.add_location(city, default_lat, default_lon)
        except (psycopg2.DatabaseError, GeopyError) as e:
            logger.error(f"Error ensuring default coordinates: {e}")
        return default_lat, default_lon

    def add_location(self, city, lat, lon):
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql.SQL('INSERT INTO locations (city, latitude, longitude) VALUES (%s, %s, %s) ON CONFLICT (city) DO UPDATE SET latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude'),
                                   (city, lat, lon))
                    conn.commit()
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error during insert: {e}")

    def get_location(self, city_country):
        try:
            city = city_country
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(sql.SQL('SELECT latitude, longitude FROM locations WHERE city = %s'), (city,))
                    result = cursor.fetchone()
                    if result:
                        return (*result, True)
                    else:
                        location = self.geocode(city_country)
                        if location:
                            lat, lon = location.latitude, location.longitude
                            self.add_location(city, lat, lon)
                            return lat, lon, True
                        else:
                            return (self.default_lat, self.default_lon, False)
        except (psycopg2.DatabaseError, GeopyError) as e:
            logger.error(f"Geocoding error: {e}")
            return (self.default_lat, self.default_lon, False)
