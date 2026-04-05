from flask_caching import Cache
import zlib
import msgpack
from config import Config


# We initialize with a simple instance and will bind it to the app in app.py
cache = Cache()


def _compress(data):
    return zlib.compress(msgpack.packb(data))

def _decompress(data):
    return msgpack.unpackb(zlib.decompress(data))
    

# For helper methods or specific logic if needed
class CacheService:
    @staticmethod
    def cache_set(key, value, timeout=Config.CACHE_LIST_TIMEOUT):
        compressed = _compress(value)
        cache.set(key, compressed, timeout=timeout)

    @staticmethod
    def cache_get(key):
        data = cache.get(key)
        if data:
            return _decompress(data)
        return None

    @staticmethod
    def cache_delete(key):
        return cache.delete(key)

    @staticmethod
    def cache_clear():
        return cache.clear()


