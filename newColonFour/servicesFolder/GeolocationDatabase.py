import sqlite3
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeopyError
import logging

logger = logging.getLogger(__name__)


class GeolocationDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
        self.geolocator = Nominatim(user_agent="your_user_agent_here")  # Adjust your user agent
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)
        # Ensuring Paris, France is added during initialization and storing its coordinates for fallback
        self.default_lat, self.default_lon = self.getDefaultCoordinates() 


    def init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS locations (
                        city TEXT PRIMARY KEY,
                        latitude REAL,
                        longitude REAL
                    )
                ''')
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error: {e}")
            # Consider logging this error or raising a custom exception

    def getDefaultCoordinates(self):
        """Ensure Paris, France is in the database and return its coordinates.
        If not present, add it and then return its coordinates."""
        city = "Paris, France"
        default_lat, default_lon = None, None  # Default values in case of failure
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT latitude, longitude FROM locations WHERE city = ?', (city,))
                result = cursor.fetchone()
                if result:
                    default_lat, default_lon = result
                else:
                    # Geocode and add Paris if not found
                    location = self.geocode(city)
                    if location:
                        default_lat, default_lon = location.latitude, location.longitude
                        self.add_location(city, default_lat, default_lon)
        except (sqlite3.DatabaseError, GeopyError) as e:
            logger.error(f"Error ensuring default coordinates: {e}")
        # Handle or log the database error appropriately
        return default_lat, default_lon

    def add_location(self, city, lat, lon):
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Start a transaction explicitly
                conn.execute('BEGIN')
                try:
                    cursor = conn.cursor()
                    cursor.execute('INSERT OR REPLACE INTO locations (city, latitude, longitude) VALUES (?, ?, ?)',
                            (city, lat, lon))
                    # Commit the transaction if the insert succeeds
                    conn.commit()
                except sqlite3.DatabaseError as e:
                    # Rollback the transaction on error
                    conn.rollback()
                    print(f"Database error during insert: {e}")
                    # Optionally, re-raise the exception or handle it as per your application's error handling policy
        except sqlite3.DatabaseError as e:
            logger.error(f"Database connection error: {e}")
            # Handle connection errors here

    def get_location(self, city_country):
        try:
            city, country = city_country.split(", ")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT latitude, longitude FROM locations WHERE city = ?', (city,))
                result = cursor.fetchone()

                if result:
                    return (*result, True)  # Return lat, lon, and success as True
                else:
                    try:
                        location = self.geocode(city_country)
                        if location:
                            lat, lon = location.latitude, location.longitude
                            self.add_location(city, lat, lon)
                            return lat, lon, True
                        else:
                            return (self.default_lat, self.default_lon, False)
                    except GeopyError as e:
                        logger.error(f"Geocoding error: {e}")
                        # Fallback to default coordinates with success as False
                        return (self.default_lat, self.default_lon, False)
        except sqlite3.DatabaseError as e:
            logger.error(f"Database error: {e}")
            # Database operation failed, fallback to default coordinates with success as False
            return (self.default_lat, self.default_lon, False)
