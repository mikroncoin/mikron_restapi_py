import time

# Cache key-value pairs in memory (a dict), with an expiry

__cache = {}

# Get the cache entry, value if returned if valid entry found in cache, otherwise None
def get_cache_entry(key):
    try:
        if key not in __cache:
            #print("Cache: Not found", key)
            return None
        # found in cache
        c = __cache[key]
        ctime = c['t']
        cval = c['v']
        now = time.time()
        if ctime < now:
            # expired, remove
            #print("Cache: Found, but expired", key, c, now)
            __cache[key] = None
            return None
        # found and valid
        #print("Cache: Found", key, c, now)
        return cval
    except:
        return None

# Add a cache entry.  Expiry is time to keep in cache, in secs.
def add_cache_entry(key, val, expiry_secs = 300):
    try:
        expiry = time.time() + expiry_secs
        __cache[key] = {'v': val, 't': expiry}
        #print("Cache: Added", key, __cache[key], expiry_secs)
    except:
        print("exception add_cache_entry")
        return
