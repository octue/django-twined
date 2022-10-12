import os


def get_db_conf():
    """
    Configures database according to the DATABASE_ENGINE environment
    variable. Defaults to SQlite.
    This method is used to let tests run against different database backends.
    """
    database_engine = os.environ.get("DATABASE_ENGINE", "postgres")
    if database_engine == "postgres":
        return {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "postgres_db",
            "USER": "postgres_user",
            "PASSWORD": "postgres_password",
            "HOST": "localhost",
            "PORT": "5432",
        }
    # elif database_engine == "sqlite":
    #     return {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
    else:
        raise ValueError(
            "Sqlite or other databases not supported for testing - see https://github.com/octue/django-twined/issues/24"
        )


DEBUG = True

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = PROJECT_DIR

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "django_extensions",  # Gives us shell_plus and reset_db for manipulating the test server
    "django_twined",
    "tests.server.example",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(PROJECT_DIR, "django_twined", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": get_db_conf()}

ROOT_URLCONF = "tests.server.urls"

STATIC_URL = "static_test/"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECRET_KEY = "secretkey"

ASGI_APPLICATION = "tests.server.asgi.application"

GCP_STORAGE_EXTRA_STORES = {"django-twined-concrete-store": {"bucket_name": "test-django-twined"}}

# MEDIA FILES
DEFAULT_FILE_STORAGE = "django_gcp.storage.GoogleCloudMediaStorage"
GCP_STORAGE_MEDIA = {"bucket_name": "example-media-assets"}
MEDIA_URL = f"https://storage.googleapis.com/{GCP_STORAGE_MEDIA['bucket_name']}/"
MEDIA_ROOT = "/media/"

# STATIC FILES
STATICFILES_STORAGE = "django_gcp.storage.GoogleCloudStaticStorage"
GCP_STORAGE_STATIC = {"bucket_name": "example-static-assets"}
STATIC_URL = f"https://storage.googleapis.com/{GCP_STORAGE_STATIC['bucket_name']}/"
STATIC_ROOT = "/static/"


# DJANGO TWINED
TWINED_BASE_URL = "https://my-server.com"

TWINED_DEFAULT_NAMESPACE = "test-default-namespace"
TWINED_DEFAULT_PROJECT_NAME = "test-default-project-name"
TWINED_DEFAULT_TAG = "test-default-tag"

TWINED_DATA_STORES = {
    "django-twined-concrete-store": {
        "model": "tests.server.example.ConcreteSynchronisedDatastore",
        "storage": "django_gcp.storage.GoogleCloudStorage",
        "storage_settings": {
            "bucket_name": "test-django-twined-concrete-store",
            "project_id": "twined-314619",
            "file_overwrite": True,
        },
    }
}
