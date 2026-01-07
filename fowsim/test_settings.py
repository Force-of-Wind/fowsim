"""
Django test settings - uses SQLite for testing.
"""

import os

# Set required environment variables before importing main settings
os.environ.setdefault("DJANGO_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASS", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")

# Import everything from main settings
from fowsim.settings import *  # noqa: F401, F403

# Override database to use SQLite (file-based for migration compatibility)
import tempfile

_test_db_path = os.path.join(tempfile.gettempdir(), "fowsim_test.sqlite3")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _test_db_path,
        "TEST": {
            "NAME": _test_db_path,
        },
    }
}

# Disable debug toolbar for tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]  # noqa: F405
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]  # noqa: F405

# Use test URLs that don't include debug_toolbar
ROOT_URLCONF = "fowsim.test_urls"

# Skip migrations for legacy game app (use None to disable migrations)
MIGRATION_MODULES = {
    "game": None,
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable logging during tests
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {},
    "root": {
        "handlers": [],
    },
}
