import time
from config import Config

class CacheService:
    def __init__(self):
        self._cache = {}
        self._timeout = Config.CACHE_TIMEOUT

    def get(self, key):
        """Retrieve a value from the cache if it hasn't expired."""
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item['expiry']:
                return item['value']
            else:
                del self._cache[key]
        return None

    def set(self, key, value):
        """Store a value in the cache with the default timeout."""
        self._cache[key] = {
            'value': value,
            'expiry': time.time() + self._timeout
        }

    def clear(self):
        """Clear all cached items."""
        self._cache = {}

# Singleton instance
cache = CacheService()
