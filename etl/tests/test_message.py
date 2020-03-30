import datetime as dt
from unittest import mock

from etl.message.forms import ArchiveMessageForm


def test_valid_delivery_time(test_archive, archive_msg):
    """Normal datetime should result in valid form"""
    archive_msg.delivery_time = dt.datetime(2019, 1, 1, 3, 0, 0)
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid(), form.errors


def test_body__null_chars(test_archive, archive_msg):
    test_archive.format_message.return_value = "Hi\x00there"
    form = ArchiveMessageForm(archive=test_archive, archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["body"] == "Hithere"


def test_body__clean_script_html(test_archive, archive_msg, html_file):
    test_archive.format_message.return_value = html_file
    form = ArchiveMessageForm(archive=test_archive, archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert "<script>I'm bad</script>" not in form.cleaned_data["body"]
    assert "I'm bad" not in form.cleaned_data["body"]
    assert "I'm fine" in form.cleaned_data["body"]


def test_body__clean_img_html(test_archive, archive_msg, html_file):
    test_archive.format_message.return_value = html_file
    form = ArchiveMessageForm(archive=test_archive, archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert (
        '<img src="http://example.com/images/img0001.png">'
        not in form.cleaned_data["body"]
    )
    assert (
        """<span alt="test image" class="__RATOM__former-img" height="10" src="http://example.com/images/img0001.png" width="10">img0001.png</span>"""
        in form.cleaned_data["body"]
    )


def test_sent_date__make_aware_fails(test_archive, archive_msg):
    """form should still be valid if make_aware fails."""
    with mock.patch("etl.message.forms.make_aware", side_effect=Exception):
        form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
        assert form.is_valid(), form.errors
        assert not form.cleaned_data["sent_date"]
        assert len(form.msg_errors) == 1
