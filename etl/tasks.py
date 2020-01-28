import logging

from celery import shared_task
from etl.importer import import_psts

logger = logging.getLogger(__name__)


@shared_task
def import_file_task(path, account, clean=False):
    logger.info(path)
    import_psts(paths=path, account=account, clean=clean, is_background=True)
