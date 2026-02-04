"""
Base settings shared across all environments.
"""
import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

# Read .env file if it exists
env_file = BASE_DIR.parent / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-change-me")

DEBUG = env("DJANGO_DEBUG")

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# Application definition
INSTALLED_APPS = [
    # Unfold must be before django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    # Django built-in
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_htmx",
    "django_otp",
    "django_otp.plugins.otp_totp",
    # Local apps
    "apps.accounts",
    "apps.tenants",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "apps.tenants.middleware.ActiveTenantMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.tenants.context_processors.tenant_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database - configured per environment
DATABASES = {
    "default": {
        "ENGINE": env("DATABASE_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DATABASE_NAME", default=str(BASE_DIR / "db.sqlite3")),
        "USER": env("DATABASE_USER", default=""),
        "PASSWORD": env("DATABASE_PASSWORD", default=""),
        "HOST": env("DATABASE_HOST", default=""),
        "PORT": env("DATABASE_PORT", default=""),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR.parent / "staticfiles"

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# Unfold admin
UNFOLD = {
    "SITE_TITLE": "Django Base App",
    "SITE_HEADER": "Django Base App",
    "SITE_SYMBOL": "dashboard",
}
