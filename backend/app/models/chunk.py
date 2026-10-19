
from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    chunk_id: str
    source: str
    page_number: int
    chunk_index: int
    text: str
    score: float = field(default=0.0, compare=False)
