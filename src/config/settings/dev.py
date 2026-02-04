"""
Development settings - SQLite, debug toolbar.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

INSTALLED_APPS += [  # noqa: F405
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
