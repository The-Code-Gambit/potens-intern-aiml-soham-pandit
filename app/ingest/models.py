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

    # Original extracted text
    text: str

    # Filled by cleaner.py
    cleaned_text: str = ""

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
    
@dataclass(slots=True)
class Chunk:
    """
    Represents one semantic chunk.
    """

    chunk_id: str

    document_id: str

    file_name: str

    text: str

    token_count: int

    page_start: int

    page_end: int

    chunk_number: int

    metadata: Dict[str, Any] = field(default_factory=dict)