"""
Base settings for django-validator.
"""

DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = 'TEST'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default_loc_mem',
    },
}