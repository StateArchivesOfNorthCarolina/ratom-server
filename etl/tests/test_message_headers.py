import pytest

from etl.message.headers import MessageHeader


class TestHeaders:
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
                "kate symes 6-27-02.nsf",
            ),
        ],
    )
    def test_parsed_headers(self, line, key, val):
        """Ensure header lines are parsed into expected key/value pairs."""
        headers = MessageHeader(line)
        assert headers.get_header(key) == val
