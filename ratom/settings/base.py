import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.humanize",
    "django.contrib.sitemaps",
    "django.contrib.postgres",
    "rest_framework",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
    "core",
    "api",
    "etl",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

PAGINATION_PAGE_SIZE = 4

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": PAGINATION_PAGE_SIZE,
    "ORDERING_PARAM": "ordering",
}

# Elasticsearch configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "localhost:9200")
ELASTICSEARCH_DSL = {
    "default": {"hosts": ELASTICSEARCH_URL},
}
ELASTICSEARCH_INDEX_NAMES = {
    "api.documents.message": "message",
}
ELASTICSEARCH_LOG_QUERIES = os.getenv("ELASTICSEARCH_LOG_QUERIES", "false") == "true"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        seconds=int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_SECONDS", 300))  # 5 minutes
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        minutes=int(
            os.getenv("JWT_REFRESH_TOKEN_LIFETIME_MINUTES", 60 * 24 * 7)  # 7 days
        )
    ),
}

ROOT_URLCONF = "ratom.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates"),],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "dealer.contrib.django.context_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "ratom.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "ratom",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "public", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/media/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "basic": {"format": "%(asctime)s %(name)-20s %(levelname)-8s %(message)s",},
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "basic",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "api": {"level": "DEBUG", "handlers": ["console"], "propagate": False,},
    },
    "root": {"handlers": ["console",], "level": "INFO",},
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"
LOCALE_PATHS = (os.path.join(PROJECT_ROOT, "locale"),)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "public", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/django-static/"

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# If using Celery, tell it to obey our logging configuration.
CELERYD_HIJACK_ROOT_LOGGER = False

# https://docs.djangoproject.com/en/1.9/topics/auth/passwords/#password-validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# Make things more secure by default. Run "python manage.py check --deploy"
# for even more suggestions that you might want to add to the settings, depending
# on how the site uses SSL.
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
AUTH_USER_MODEL = "core.User"

ATTACHMENT_PATH = "attachments/"

BROKER_URL = os.getenv("BROKER_URL")
if BROKER_URL:
    CELERY_BROKER_URL = f"redis://{BROKER_URL}:6379/0"
    CELERY_WORKER_REDIRECT_STDOUTS = True
    CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = "INFO"
    # If using Celery, tell it to obey our logging configuration.
    CELERY_WORKER_HIJACK_ROOT_LOGGER = False
    CELERY_WORKER_LOG_FORMAT = (
        "[%(asctime)s: %(levelname)s/%(processName)s/%(name)s] %(message)s"
    )
