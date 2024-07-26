# newColonFour/apps.py
from django.apps import AppConfig
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class NewcolonfourConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newColonFour"

    def ready(self):
        super().ready()
        try:
            cache.set('redis_connection_test', 'connected', timeout=1)
            value = cache.get('redis_connection_test')
            if value == 'connected':
                logger.debug("Successfully connected to Redis!")
            else:
                logger.debug("Failed to connect to Redis.")
        except Exception as e:
            logger.debug(f"Error connecting to Redis: {e}")
