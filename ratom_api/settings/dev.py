# flake8: noqa
import os
import sys

from ratom_api.settings.base import *  # noqa

DEBUG = True

INSTALLED_APPS += ("debug_toolbar",)
MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

INTERNAL_IPS = ("127.0.0.1",)

#: Don't send emails, just print them on stdout
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

#: Run celery tasks synchronously
CELERY_ALWAYS_EAGER = True

#: Tell us when a synchronous celery task fails
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

SECRET_KEY = os.environ.get(
    "SECRET_KEY", "#bd9o-0&)wpy=uhy*#zc7ppe05h8b^f68+&hv7dzs5qf&t@gq6"
)

# Special test settings
if "test" in sys.argv:
    PASSWORD_HASHERS = (
        "django.contrib.auth.hashers.SHA1PasswordHasher",
        "django.contrib.auth.hashers.MD5PasswordHasher",
    )

    LOGGING["root"]["handlers"] = []

GRAPHQL_JWT = {
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_EXPIRATION_DELTA": timedelta(days=365),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=365 * 7),
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "ratomapi",
        "USER": "postgres",
        "HOST": "localhost",
        "PORT": "54330",
    }
}
