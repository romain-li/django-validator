"""
Test specific Django settings.
"""

# Inherit from base settings
from .base import *

USE_18N = False

# Change test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    },
    'replica': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST': {
            'MIRROR': 'default',
        },
    },
}

# Configure nose
NOSE_ARGS = []

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Install test-specific Django apps
# INSTALLED_APPS += ('django_nose',)