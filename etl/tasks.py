from celery import shared_task
from etl.importer import import_psts


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
