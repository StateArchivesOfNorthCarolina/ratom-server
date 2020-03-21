from email.message import EmailMessage
from typing import Dict


class MessageHeader:
    """Provides a consistent interface to the mail and MIME headers from a pypff message.
    Currently takes a headers only parse of the pypff message headers.
    """

    def __init__(self, message: EmailMessage) -> None:
        self.raw_headers = message.items()
        self.parsed_headers: Dict[str, str] = {}
        self.decompose_headers()

    def decompose_headers(self) -> None:
        """Python's EmailMessage items() returns a list of tuples.
        """
        if self.raw_headers:
            self.parsed_headers = {i[0].lower(): i[1] for i in self.raw_headers}

    def get_header(self, key: str) -> str:
        return self.parsed_headers.get(key.lower(), "")

    def get_full_headers(self) -> dict:
        return self.parsed_headers
