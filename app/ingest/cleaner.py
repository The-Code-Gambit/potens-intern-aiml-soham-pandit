"""
Text Cleaning Pipeline

Responsible for preparing extracted document text
before chunking.

This module intentionally preserves semantic meaning
while removing formatting noise.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List

from app.core.logger import get_logger
from app.ingest.models import Page

logger = get_logger(__name__)


class TextCleaner:
    """
    Cleans extracted document pages.

    The cleaner is intentionally conservative.

    It removes formatting artefacts while preserving
    headings, punctuation, equations and paragraphs.
    """

    def clean_pages(self, pages: List[Page]) -> List[Page]:
        """
        Clean every page.
        """

        logger.info("Cleaning %d pages", len(pages))

        for page in pages:

            cleaned = page.text

            cleaned = self._normalize_unicode(cleaned)

            cleaned = self._fix_hyphenation(cleaned)

            cleaned = self._normalize_whitespace(cleaned)

            cleaned = self._remove_page_artifacts(cleaned)

            cleaned = self._normalize_paragraphs(cleaned)

            page.cleaned_text = cleaned

        return pages
    
    def _normalize_unicode(self, text: str) -> str:
     """
     Normalize Unicode characters.
     """

     return unicodedata.normalize("NFKC", text)
 
    def _fix_hyphenation(self, text: str) -> str:
     """
     Merge words split across lines by PDF extraction.
     """

     return re.sub(r"(\w)-\n(\w)", r"\1\2", text)
 
    def _normalize_whitespace(self, text: str) -> str:
     """
     Remove unnecessary whitespace.
     """

     text = re.sub(r"[ \t]+", " ", text)

     text = re.sub(r"\n{3,}", "\n\n", text)

     return text.strip()
 
    def _remove_page_artifacts(self, text: str) -> str:
     """
     Remove obvious page numbers.
     """

     lines = []

     for line in text.splitlines():

        stripped = line.strip()

        if stripped.isdigit():
            continue

        lines.append(line)

     return "\n".join(lines)
 
    def _normalize_paragraphs(self, text: str) -> str:
     """
     Preserve paragraph spacing.
     """

     paragraphs = []

     for paragraph in text.split("\n\n"):

        paragraph = paragraph.strip()

        if paragraph:

            paragraphs.append(paragraph)

     return "\n\n".join(paragraphs)