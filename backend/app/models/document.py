
from dataclasses import dataclass


@dataclass
class DocumentPage:
    source: str
    page_number: int
    text: str
