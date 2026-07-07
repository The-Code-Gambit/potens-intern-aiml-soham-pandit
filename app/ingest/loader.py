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

import hashlib

import fitz  # PyMuPDF

from app.ingest.exceptions import (
    CorruptedDocumentError,
    EmptyDocumentError,
    EncryptedDocumentError,
)

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
     Load a PDF document page by page.

     Returns
     -------
     List[Page]

     Raises
     ------
     CorruptedDocumentError
     EncryptedDocumentError
     EmptyDocumentError
     """

     logger.info("Opening PDF: %s", file_path)

     try:
        document = fitz.open(file_path)

     except Exception as exc:
        logger.exception("Failed to open PDF.")
        raise CorruptedDocumentError(str(exc)) from exc

     if document.needs_pass:
        raise EncryptedDocumentError(
            f"{file_path.name} is password protected."
        )

     document_id = self._generate_document_id(file_path)

     pages: List[Page] = []

     metadata = document.metadata

     for page_index in range(document.page_count):

        page = document.load_page(page_index)

        text = page.get_text("text")

        if not text.strip():
            logger.warning(
                "Skipping empty page %d",
                page_index + 1,
            )
            continue

        pages.append(
            Page(
                document_id=document_id,
                file_name=file_path.name,
                file_path=file_path,
                page_number=page_index + 1,
                text=text,
                metadata={
                    "title": metadata.get("title"),
                    "author": metadata.get("author"),
                    "subject": metadata.get("subject"),
                },
            )
        )

     document.close()

     if not pages:
        raise EmptyDocumentError(
            f"No extractable text found in {file_path.name}"
        )

     logger.info(
        "Loaded %d pages from %s",
        len(pages),
        file_path.name,
     )

     return pages

    def _load_txt(self, file_path: Path) -> List[Page]:
     """
     Load a plain text file.
     """

     logger.info("Opening text file: %s", file_path)

     try:

        text = file_path.read_text(
            encoding="utf-8"
        )

     except UnicodeDecodeError as exc:
        raise DocumentLoaderError(
            "Unable to decode text file."
        ) from exc

     if not text.strip():
        raise EmptyDocumentError(
            f"{file_path.name} is empty."
        )

     return [
        Page(
            document_id=self._generate_document_id(file_path),
            file_name=file_path.name,
            file_path=file_path,
            page_number=1,
            text=text,
            metadata={},
        )
     ]
        
    def _generate_document_id(self, file_path: Path) -> str:
       """
        Generate a stable document ID using the SHA-256 hash of the file contents.
       """

       sha256 = hashlib.sha256()

       with file_path.open("rb") as file:
        while chunk := file.read(8192):
            sha256.update(chunk)

       return sha256.hexdigest()    