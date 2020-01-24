import re
from typing import Dict


class MessageHeader:
    """Provides a consistent interface to the mail and MIME headers from a pypff message.
    """

    def __init__(self, headers: str) -> None:
        self.raw_headers = headers
        self.parsed_headers: Dict[str, str] = {}
        self.decompose_headers()

    def decompose_headers(self) -> None:
        """[summary]
        """
        if self.raw_headers:
            decomp = re.split(
                r"\r\n", re.sub(r"\r\n\s", "\t", self.raw_headers.strip())
            )
            for header_item in decomp:
                s = header_item.split(":", 1)
                key = s[0].lower()
                val = s[1].lstrip()
                self.parsed_headers[key] = val

    def get_header(self, key: str) -> str:
        return self.parsed_headers.get(key.lower(), "")

    def get_full_headers(self) -> str:
        return self.parsed_headers
