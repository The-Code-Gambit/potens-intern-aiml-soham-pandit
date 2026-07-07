"""
Document Loader

Responsible for loading supported documents into
structured Page objects.

Current supported formats:
- PDF
- TXT

Responsibilities:
- Validate file path
- Validate file type
- Route to the appropriate loader

This module does NOT perform:
- Text cleaning
- Chunking
- Embedding
"""

from pathlib import Path
from typing import List

from app.core.logger import get_logger
from app.ingest.exceptions import (
    DocumentLoaderError,
    UnsupportedFileTypeError,
)
from app.ingest.models import Page

logger = get_logger(__name__)


class DocumentLoader:
    """
    Loads supported document formats and returns Page objects.

    The actual parsing logic for PDF/TXT is implemented in
    dedicated private methods.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}

    def load_document(self, file_path: Path) -> List[Page]:
        """
        Load a document and dispatch it to the appropriate loader.

        Parameters
        ----------
        file_path : Path
            Path to the input document.

        Returns
        -------
        List[Page]
            Extracted pages.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.

        UnsupportedFileTypeError
            If the extension is unsupported.
        """

        logger.info("Loading document: %s", file_path)

        self._validate_file(file_path)

        extension = file_path.suffix.lower()

        if extension == ".pdf":
            return self._load_pdf(file_path)

        if extension == ".txt":
            return self._load_txt(file_path)

        raise UnsupportedFileTypeError(
            f"Unsupported document type: {extension}"
        )

    def _validate_file(self, file_path: Path) -> None:
        """
        Validate that the document exists and is supported.
        """

        if not file_path.exists():
            logger.error("File not found: %s", file_path)
            raise FileNotFoundError(file_path)

        if not file_path.is_file():
            logger.error("Not a valid file: %s", file_path)
            raise DocumentLoaderError(
                f"{file_path} is not a file."
            )

        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.error("Unsupported extension: %s", file_path.suffix)
            raise UnsupportedFileTypeError(
                f"Unsupported extension: {file_path.suffix}"
            )

    def _load_pdf(self, file_path: Path) -> List[Page]:
        """
        Placeholder for PDF loading.

        Will be implemented in the next commit.
        """

        logger.info("PDF loader invoked for %s", file_path)

        raise NotImplementedError(
            "PDF loading not implemented yet."
        )

    def _load_txt(self, file_path: Path) -> List[Page]:
        """
        Placeholder for TXT loading.

        Will be implemented in the next commit.
        """

        logger.info("TXT loader invoked for %s", file_path)

        raise NotImplementedError(
            "TXT loading not implemented yet."
        )