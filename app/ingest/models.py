from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any


@dataclass(slots=True)
class Page:
    """
    Represents a single extracted page from a document.
    """

    document_id: str
    file_name: str
    file_path: Path

    page_number: int

    text: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DocumentInfo:
    """
    Metadata about an ingested document.
    """

    document_id: str

    file_name: str

    file_path: Path

    total_pages: int

    file_size: int