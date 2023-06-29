import logging

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


VERBOSITY_MAP = {
    0: logging.ERROR,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}


class Command(BaseCommand):
    """Use `python manage.py help sync_data_stores` to display help for this command line administration tool"""

    help = (
        "Syncs files and their metadata from stores (defined in SETTINGS) into queryable records in the database."
        "Use in development for repopulating an empty database with the contents of the store(s),"
        "or use in production if a migration is applied to metadata stored in the database and you need to"
        "propagate that to the store"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-keys",
            nargs="+",
            required=False,
            dest="source_keys",
            default=None,
            help="Specify the data store keys. If none, all keys specified in settings.TWINED_DATA_STORES will be used.",
        )
        parser.add_argument(
            "--db-to-store",
            required=False,
            dest="source_keys",
            default=None,
            help="By default, metadata is synced from store to db. To do the other way arou",
        )

    def handle(self, *args, source_keys=None, **options):

        # Ensure we respect the --verbosity command option
        verbosity = int(options["verbosity"])
        logger.setLevel(VERBOSITY_MAP[verbosity])

        # Get the data sources to synchronise (by default, all defined)
        source_keys = source_keys or settings.TWINED_DATA_STORES.keys()
        stores = dict((key, settings.TWINED_DATA_STORES[key]) for key in source_keys)

        # Loop through the data sources
        for key, store in stores.items():
            logger.info("Synchronizing store -> database for %s", key)

            # Get model class and the storage instance used for its datafiles
            Model = apps.get_model(*store["model"].split("."))

            # Daisychain sync commands so the store comparison only gets run once
            Model.objects.import_missing().delete_missing().sync_metadata_from_store()
