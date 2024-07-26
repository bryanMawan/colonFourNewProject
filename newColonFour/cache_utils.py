# yourapp/cache_utils.py
import hashlib
from django.core.cache import cache

def set_cache_with_prefix(prefix, key, value, timeout=None):
    full_key = f"{prefix}:{key}"
    cache.set(full_key, value, timeout)
    print(f"Set cache for key: {full_key}")

def get_cache_with_prefix(prefix, key):
    print(f"Getting cache with {prefix} ")
    full_key = f"{prefix}:{key}"
    value = cache.get(full_key)
    print(f"Get cache for key: {full_key}")
    return value

def generate_cache_key(search_query, order_by, filters):
    # Create a unique key based on search query, filters, and order_by
    key_string = f"event_ajax_view_{search_query}_{order_by}_{filters}"
    print("Initial query key string: key_string")
    # Use hashlib to create a hash of the key string
    return hashlib.md5(key_string.encode()).hexdigest()
