# flake8: noqa

# Settings for live deployed environments: vagrant, staging, production, etc
import os

from .base import *  # noqa

os.environ.setdefault("CACHE_HOST", "127.0.0.1:11211")
os.environ.setdefault("BROKER_HOST", "127.0.0.1:5672")

#: deploy environment - e.g. "staging" or "production"
ENVIRONMENT = os.environ["ENVIRONMENT"]


DEBUG = os.getenv("DJANGO_DEBUG") == "1"


if "MEDIA_ROOT" in os.environ:
    MEDIA_ROOT = os.getenv("MEDIA_ROOT")


if "DATABASE_URL" in os.environ:
    # Dokku
    SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

    import dj_database_url

    # Update database configuration with $DATABASE_URL.
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES["default"].update(db_from_env)

    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    INSTALLED_APPS.remove("django.contrib.staticfiles")
    INSTALLED_APPS.extend(
        ["whitenoise.runserver_nostatic", "django.contrib.staticfiles",]
    )

    MIDDLEWARE.remove("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
    ] + MIDDLEWARE

    # Allow all host headers (feel free to make this more specific)
    ALLOWED_HOSTS = ["*"]

    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    WEBSERVER_ROOT = os.path.join(PROJECT_ROOT, "www")
else:
    SECRET_KEY = os.environ["SECRET_KEY"]

    DATABASES["default"]["NAME"] = "ratom_%s" % ENVIRONMENT.lower()
    DATABASES["default"]["USER"] = "ratom_%s" % ENVIRONMENT.lower()
    DATABASES["default"]["HOST"] = os.environ.get("DB_HOST", "")
    DATABASES["default"]["PORT"] = os.environ.get("DB_PORT", "")
    DATABASES["default"]["PASSWORD"] = os.environ.get("DB_PASSWORD", "")

    WEBSERVER_ROOT = "/var/www/ratom/"

PUBLIC_ROOT = os.path.join(WEBSERVER_ROOT, "public")

STATIC_ROOT = os.path.join(PUBLIC_ROOT, "static")

MEDIA_ROOT = os.path.join(PUBLIC_ROOT, "media")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "%(CACHE_HOST)s" % os.environ,
    }
}

EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = os.environ.get("EMAIL_USE_SSL", False)
# use TLS or SSL, not both:
assert not (EMAIL_USE_TLS and EMAIL_USE_SSL)
if EMAIL_USE_TLS:
    default_smtp_port = 587
elif EMAIL_USE_SSL:
    default_smtp_port = 465
else:
    default_smtp_port = 25
EMAIL_PORT = os.environ.get("EMAIL_PORT", default_smtp_port)
EMAIL_SUBJECT_PREFIX = "[Ratom_Api %s] " % ENVIRONMENT.title()
DEFAULT_FROM_EMAIL = "noreply@%(DOMAIN)s" % os.environ
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True

ALLOWED_HOSTS = [os.environ["DOMAIN"]]

# Use template caching on deployed servers
for backend in TEMPLATES:
    if backend["BACKEND"] == "django.template.backends.django.DjangoTemplates":
        default_loaders = ["django.template.loaders.filesystem.Loader"]
        if backend.get("APP_DIRS", False):
            default_loaders.append("django.template.loaders.app_directories.Loader")
            # Django gets annoyed if you both set APP_DIRS True and specify your own loaders
            backend["APP_DIRS"] = False
        loaders = backend["OPTIONS"].get("loaders", default_loaders)
        for loader in loaders:
            if (
                len(loader) == 2
                and loader[0] == "django.template.loaders.cached.Loader"
            ):
                # We're already caching our templates
                break
        else:
            backend["OPTIONS"]["loaders"] = [
                ("django.template.loaders.cached.Loader", loaders)
            ]


# Environment overrides
# These should be kept to an absolute minimum
if ENVIRONMENT.upper() == "LOCAL":
    # Don't send emails from the Vagrant boxes
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


if "DOKKU_NGINX_SSL_PORT" in os.environ:
    # Dokku with SSL
    # SECURE_SSL_REDIRECT = True
    # Try HTTP Strict Transport Security (increase time if everything looks okay)
    # SECURE_HSTS_SECONDS = 1800
    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_REDIRECT_EXEMPT = ["/.well-known"]  # For Let's Encrypt


SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])

AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

if "amazonaws.com" in ELASTICSEARCH_URL:
    from boto3 import session
    from requests_aws_sign import AWSV4Sign
    from elasticsearch import RequestsHttpConnection

    session = session.Session()
    credentials = session.get_credentials()
    region = session.region_name or AWS_S3_REGION_NAME
    http_auth = AWSV4Sign(credentials, region, "es")
    ELASTICSEARCH_DSL = {
        "default": {
            "hosts": ELASTICSEARCH_URL,
            "http_auth": http_auth,
            "connection_class": RequestsHttpConnection,
            "port": 433,
            "use_ssl": True,
            "verify_ssl": True,
        },
    }
