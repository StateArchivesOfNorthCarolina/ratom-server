import datetime as dt

from etl.message.forms import ArchiveMessageForm


def test_valid_delivery_time(test_archive, archive_msg):
    """Normal datetime should result in valid form"""
    archive_msg.delivery_time = dt.datetime(2019, 1, 1, 3, 0, 0)
    form = ArchiveMessageForm(archive=test_archive, archive_msg=archive_msg)
    assert form.is_valid()


def test_body__null_chars(test_archive, archive_msg):
    archive_msg.plain_text_body = "Hi\x00there"
    test_archive.format_message.return_value = archive_msg.plain_text_body
    form = ArchiveMessageForm(archive=test_archive, archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["body"] == "Hithere"
