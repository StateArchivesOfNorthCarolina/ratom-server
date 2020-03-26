from celery import shared_task
from celery.utils.log import logger
from etl.importer import import_psts

from core.models import File


@shared_task
def import_file_task(
    paths: [str], account: str, clean=False, clean_file=False, is_remote=True
):
    import_psts(
        paths=paths,
        account=account,
        clean=clean,
        clean_file=clean_file,
        is_background=True,
        is_remote=True,
    )


@shared_task
def remove_file_task(files: []):
    for f in files:
        remove = File.objects.filter(id=f).first()
        logger.info(
            f"Recovering {remove.account.title} by removing failed file: {remove.filename}"
        )
        if remove:
            remove.delete()
