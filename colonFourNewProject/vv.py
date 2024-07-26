import psycopg2
from psycopg2 import sql
import logging
from decouple import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def clean_location_table():
    connection_params = {
            "dbname": config('TEST_DB_NAME'),
            "user": config('TEST_DB_USER'),
            "password": config('TEST_DB_PASSWORD'),
            "host": config('TEST_DB_HOST'),
            "port": config('TEST_DB_PORT', default="5432"),}
    
    try:
        # Connect to the database
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor() as cursor:
                logger.debug("Connected to the database.")
                
                # Delete all rows from the locations table
                cursor.execute('DELETE FROM locations')
                
                deleted_rows = cursor.rowcount
                conn.commit()
                logger.debug("Deleted %d rows from locations table.", deleted_rows)
                
                # Check if any rows remain
                cursor.execute('SELECT COUNT(*) FROM locations')
                remaining_rows = cursor.fetchone()[0]
                logger.debug("Remaining rows in locations table: %d", remaining_rows)
                
    except psycopg2.DatabaseError as e:
        logger.error(f"Database error during cleanup: {e}")

if __name__ == "__main__":
    clean_location_table()
