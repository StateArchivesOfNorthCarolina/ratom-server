from celery import shared_task
from etl.importer import import_psts


@shared_task
def import_file_task(paths, account, clean=False):
    import_psts(paths=paths, account=account, clean=clean, is_background=True)
