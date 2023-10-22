"""
Django settings for webcau project.

Generated by 'django-admin startproject' using Django 4.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os

from django.conf.global_settings import LOGOUT_REDIRECT_URL

# Read .env file
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.environ.get("DEBUG", False) == "True" else False

temp_allowed = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")
if temp_allowed[0] == "":
    ALLOWED_HOSTS = []
else:
    ALLOWED_HOSTS = temp_allowed


# Application definition

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "avisos",
    "annoying",
    "phonenumber_field",
    "compressor",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "webcau.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join((BASE_DIR), "templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "webcau.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

gettext = lambda x: x
LANGUAGE_CODE = "es-ES"
LANGUAGES = (("es", gettext("Spanish")),)

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
# Bootstrap in CSS and JS
# https://getbootstrap.com/docs/4.0/getting-started/
# Font Awesome

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]
COMPRESS_OFFLINE = os.environ.get("COMPRESS_OFFLINE")
LIBSASS_OUTPUT_STYLE = os.environ.get("LIBSASS_OUTPUT_STYLE")
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)


# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Redirection after login: it should be changed to the previous page if possible
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/acceso/login/"
LOGOUT_REDIRECT_URL = "/acceso/login/"
SESSION_COOKIE_SECURE = False

# Reset Password
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")
if os.environ.get("IS_PRODUCTION_SERVER") == "True":
    EMAIL_HOST = os.environ.get("EMAIL_HOST")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get(
        "EMAIL_HOST_PASSWORD"
    )  # Si se quiere cambiar el user y password, revisar 'https://dev.to/abderrahmanemustapha/how-to-send-email-with-django-and-gmail-in-production-the-right-way-24ab'
    EMAIL_PORT = os.environ.get("EMAIL_PORT")
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")
    DEFAULT_FROM_EMAIL = "default from email"

# CELERY STUFF
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "America/Santiago"
CELERY_ENABLE_UTC = False

if os.environ.get("IS_PRODUCTION_SERVER") == "True":
    # SENTRY STUFF
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn="https://06f1fd530cc84eec9a0affc87d9891f2@o4504063523028992.ingest.sentry.io/4504063525191680",
        integrations=[
            DjangoIntegration(),
        ],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
