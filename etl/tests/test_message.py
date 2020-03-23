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


def test_body__clean_html(test_archive, archive_msg):
    test_archive.format_message.return_value = """
        <body>
            <h1>I'm fine</h1>
            <script>I'm bad</script>
        </body>
    """
    form = ArchiveMessageForm(archive=test_archive, archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert "<script>I'm bad</script>" not in form.cleaned_data["body"]
    assert "I'm bad" not in form.cleaned_data["body"]
    assert "I'm fine" in form.cleaned_data["body"]


def test_sent_date__make_aware_fails(test_archive, archive_msg):
    """form should still be valid if make_aware fails."""
    with mock.patch("etl.message.forms.make_aware", side_effect=Exception):
        form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
        assert form.is_valid(), form.errors
        assert not form.cleaned_data["sent_date"]
        assert len(form.msg_errors) == 1


def test_headers_clean(test_archive, archive_msg):
    """Make sure transport_headers appear in cleaned_data."""
    archive_msg.transport_headers = 'From: "Lester Rawson"\r\n'
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid()
    assert "headers" in form.cleaned_data
    assert "From" in form.cleaned_data["headers"]


def test_headers_good_with_malformed_data(test_archive, archive_msg):
    """Make sure that transport headers don't blow up during import with a bad header"""
    archive_msg.transport_headers = (
        'Microsoft Mail Internet Headers Version 2.0\r\nFrom: "Lester Rawson"\r\n'
    )
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid()
    assert "headers" in form.cleaned_data
    assert "From" in form.cleaned_data["headers"]
