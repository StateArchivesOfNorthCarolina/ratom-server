import io
import logging
from hashlib import md5
import mimetypes

import pypff

from django.conf import settings
from django.core.files.storage import default_storage

from core.models import Attachment


logger = logging.getLogger(__name__)


def extract_attachment(attachment: pypff.attachment) -> str:
    """Saves the attachment if it does not already exist.
    Attachments are saved using their md5 hexdigest as a name.
    No extension is saved??
    :returns string: the hexdigest of the attachment
    """
    fo = io.BytesIO()
    hasher = md5()
    while True:
        buff = attachment.read_buffer(2048)
        if buff:
            fo.write(buff)
            hasher.update(buff)
            continue
        break
    hex_digest = hasher.hexdigest()
    path = f"{settings.ATTACHMENT_PATH}/{hex_digest}"
    if not default_storage.exists(path):
        default_storage.save(path, fo)
    fo = None
    hasher = None
    return hex_digest


def save_attachment(m):
    for a in m.attachments:  # type: pypff.attachment
        logger.info(f"Storing attachment({a.identifier}): {a.name} - {a.size}")
        hashed_name = "fixme"
        file_name = a.name
        if not file_name:
            file_name = hashed_name

        mime, encoding = mimetypes.guess_type(file_name)
        if not mime:
            mime = "Unknown"
        Attachment.objects.create(
            message=m, file_name=file_name, mime_type=mime, hashed_name=hashed_name,
        )
