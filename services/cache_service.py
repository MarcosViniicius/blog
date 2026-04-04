from flask_caching import Cache

# We initialize with a simple instance and will bind it to the app in app.py
cache = Cache()

# For helper methods or specific logic if needed
class CacheService:
    @staticmethod
    def get(key):
        return cache.get(key)

    @staticmethod
    def set(key, value, timeout=None):
        return cache.set(key, value, timeout=timeout)

    @staticmethod
    def delete(key):
        return cache.delete(key)

    @staticmethod
    def clear():
        return cache.clear()
