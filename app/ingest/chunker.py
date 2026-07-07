from __future__ import annotations

import hashlib
from typing import List

import nltk
from transformers import AutoTokenizer

from app.core.logger import get_logger
from app.ingest.models import Chunk, Page

logger = get_logger(__name__)

class SemanticChunker:
    """
    Token-aware semantic chunker.

    Strategy:

    1. Preserve paragraph boundaries
    2. Split oversized paragraphs into sentences
    3. Merge sentences until token limit
    4. Add overlap between chunks
    """

    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

    def __init__(
        self,
        chunk_size: int = 450,
        overlap: int = 80,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

        logger.info(
            "Loading tokenizer: %s",
            self.EMBEDDING_MODEL,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.EMBEDDING_MODEL
        )
        
    def _count_tokens(self, text: str) -> int:
     """
     Count tokens using the embedding tokenizer.
     """

     return len(
        self.tokenizer.encode(
            text,
            add_special_tokens=False,
        )
     )
     
    def _split_paragraphs(
     self,
     text: str,
     ) -> List[str]:
     """
     Split cleaned text into paragraphs.
     """

     return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
     ]
     
    def _split_sentences(
     self,
     paragraph: str,
     ) -> List[str]:
     """
     Split a paragraph into sentences.
     """

     return nltk.sent_tokenize(paragraph)
 
    def _generate_chunk_id(
     self,
     document_id: str,
     page: int,
     index: int,
     ) -> str:
     """
     Generate deterministic chunk IDs.
     """

     key = f"{document_id}-{page}-{index}"

     return hashlib.sha256(
        key.encode()
     ).hexdigest()
     
    def chunk_pages(
     self,
     pages: List[Page],
     ) -> List[Chunk]:
     """
     Convert cleaned pages into semantic chunks.
     """

     logger.info(
        "Chunking %d pages",
        len(pages),
     )

     chunks: List[Chunk] = []

     # Implementation comes next

     return chunks