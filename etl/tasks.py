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
    """
    Accounts have properties tied to the front-end account list widget. If there
    are no files this state crashes the UI. So, remove the account if an account
    has no files, after an attempted restore.
    """
    for f in File.objects.filter(pk__in=files):
        logger.info(
            f"Recovering {f.account.title} by removing failed file: {f.filename}"
        )
        f.import_status = File.RESTORING
        f.save()
        f.delete()
        if f.account.files.count() == 0:
            f.account.delete()
