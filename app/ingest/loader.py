"""
Document Loader

Responsible for loading supported documents into
structured Page objects.

Supported formats:

- PDF
- TXT
"""

from pathlib import Path
from typing import List

from app.ingest.models import Page
from app.core.logger import get_logger

logger = get_logger(__name__)


class DocumentLoader:
    """
    Loads documents from disk.

    Responsibilities
    ----------------

    - Validate file path
    - Validate file extension
    - Extract page-wise text
    - Return Page objects

    This class does NOT perform:

    - Cleaning
    - Chunking
    - Embedding
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".txt",
    }

    def load_document(self, file_path: Path) -> List[Page]:
        """
        Public entry point.

        Determines which loader to call.
        """

        raise NotImplementedError

    def _load_pdf(self, file_path: Path) -> List[Page]:
        """
        Load PDF pages.
        """

        raise NotImplementedError

    def _load_txt(self, file_path: Path) -> List[Page]:
        """
        Load text file.
        """

        raise NotImplementedError