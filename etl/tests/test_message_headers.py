import pytest

from etl.message.forms import ArchiveMessageForm


@pytest.mark.parametrize(
    "line,key,val",
    [
        ('from: "Lester Rawson"\r\n', "from", '"Lester Rawson"'),
        (
            "subject: Re: Unit Contingent Deals\r\n",
            "subject",
            "Re: Unit Contingent Deals",
        ),
        (
            "filename: kate symes 6-27-02.nsf  \r\n",
            "filename",
            "kate symes 6-27-02.nsf  ",
        ),
    ],
)
def test_parsed_headers(test_archive, archive_msg, line, key, val):
    """Ensure header lines are parsed into expected key/value pairs."""
    archive_msg.transport_headers = line
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["headers"][key] == val


@pytest.mark.parametrize(
    "line", ['from: "Lester Rawson"\r\n', 'From: "Lester Rawson"\r\n']
)
def test_header_key_case(test_archive, archive_msg, line):
    """Parsing headers should work for both lower and upper case use of key."""
    archive_msg.transport_headers = line
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["msg_from"] == '"Lester Rawson"'


@pytest.mark.parametrize(
    "header,form_field",
    [
        ("From", "msg_from"),
        ("To", "msg_to"),
        ("CC", "msg_cc"),
        ("BCC", "msg_bcc"),
        ("Subject", "subject"),
    ],
)
def test_header_form_field_pairing(test_archive, archive_msg, header, form_field):
    """Specific header values should end up in correct form fields."""
    archive_msg.transport_headers = f"{header}: test\r\n"
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert form.cleaned_data[form_field]


@pytest.mark.parametrize(
    "header", ["From", "To", "CC", "BCC", "Subject", "Other-Header"],
)
def test_saved_header_values(test_archive, archive_msg, header):
    """All headers should end up in the `headers` JSON field."""
    archive_msg.transport_headers = f"{header}: test\r\n"
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["headers"][header] == "test"


def test_headers_clean(test_archive, archive_msg):
    """Make sure transport_headers appear in cleaned_data."""
    archive_msg.transport_headers = 'From: "Lester Rawson"\r\n'
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid()
    assert "headers" in form.cleaned_data
    assert "From" in form.cleaned_data["headers"]


def test_expected_bad_header(test_archive, archive_msg):
    """Expected bad headers should be cleaned before conversion and processing."""
    archive_msg.transport_headers = (
        'Microsoft Mail Internet Headers Version 2.0\r\nFrom: "Lester Rawson"\r\n'
    )
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.is_valid()
    assert "headers" in form.cleaned_data
    assert "From" in form.cleaned_data["headers"]


def test_unexpected_bad_header(test_archive, archive_msg):
    """Form should pass validation even with bad headers."""
    archive_msg.transport_headers = 'Random Bad Header\r\nFrom: "Lester Rawson"\r\n'
    form = ArchiveMessageForm(archive=test_archive(), archive_msg=archive_msg)
    assert form.msg_errors
    type_, name, _ = form.msg_errors[0]
    assert name == "MissingHeaderBodySeparatorDefect"
    assert form.is_valid()
