"""
Chunking Pipeline

Responsible for splitting cleaned document pages into retrieval-ready
chunks.

Design notes
------------
Chunking is PAGE-WISE, never document-wise. Concatenating pages before
splitting would make page-level citations inaccurate, since a single
chunk could then straddle two physical pages with no reliable way to
attribute it back to one page number.

This module has three responsibilities, kept as separate small classes
so each can be tested and swapped independently (SRP):

1. TokenCounter   - wraps the BGE tokenizer, used ONLY for token counts.
2. ChunkIdBuilder  - produces deterministic SHA256 chunk ids.
3. PageChunker     - orchestrates LangChain's RecursiveCharacterTextSplitter
                     over a single page and assembles Chunk objects.

The module never writes to disk and never returns JSON. It is a pure
in-memory transformation: List[Page] -> List[Chunk].
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, PreTrainedTokenizerBase

from app.core.logger import get_logger
from app.ingest.models import Chunk, Page
from app.ingest.exceptions import ChunkingError

logger = get_logger(__name__)

DEFAULT_TOKENIZER_MODEL = "BAAI/bge-small-en-v1.5"


@dataclass(frozen=True)
class ChunkerConfig:
    """Immutable configuration for the chunking pipeline.

    Kept as its own dataclass (rather than loose constructor args) so
    the splitter's behaviour is explicit, testable, and easy to tune
    without touching PageChunker's logic.
    """

    chunk_size: int = 450
    chunk_overlap: int = 80
    separators: List[str] = field(
        default_factory=lambda: ["\n\n", "\n", ". ", " ", ""]
    )
    tokenizer_model: str = DEFAULT_TOKENIZER_MODEL


class TokenCounter:
    """Counts tokens using the BGE tokenizer.

    Isolated from PageChunker so the (relatively expensive) tokenizer
    load happens once and can be mocked out in unit tests without
    touching the splitting logic.
    """

    def __init__(self, tokenizer_model: str = DEFAULT_TOKENIZER_MODEL) -> None:
        logger.info("Loading tokenizer '%s' for token counting", tokenizer_model)
        self._tokenizer: PreTrainedTokenizerBase = AutoTokenizer.from_pretrained(
            tokenizer_model
        )

    def count(self, text: str) -> int:
        """Return the number of BGE tokens in `text`."""
        if not text:
            return 0
        return len(self._tokenizer.encode(text, add_special_tokens=False))


class ChunkIdBuilder:
    """Builds deterministic, reproducible chunk identifiers.

    Deterministic IDs (as opposed to UUIDs) let re-ingesting the same
    document produce identical chunk ids, which matters for idempotent
    upserts into ChromaDB.
    """

    @staticmethod
    def build(document_id: str, page_number: int, chunk_number: int) -> str:
        raw = f"{document_id}:{page_number}:{chunk_number}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class PageChunker:
    """Splits a single page's cleaned text into Chunk objects."""

    def __init__(self, config: ChunkerConfig, token_counter: TokenCounter) -> None:
        self._config = config
        self._token_counter = token_counter
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
        )

    def chunk(self, page: Page) -> List[Chunk]:
        """Split one page into Chunk objects. Returns [] for empty pages."""
        text = (page.cleaned_text or "").strip()

        if not text:
            logger.debug(
                "Skipping empty page %s of document '%s'",
                page.page_number,
                page.document_id,
            )
            return []

        try:
            raw_splits = self._splitter.split_text(text)
        except Exception as exc:  # noqa: BLE001 - re-raised as domain error
            raise ChunkingError(
                f"Failed to split page {page.page_number} of "
                f"document '{page.document_id}': {exc}"
            ) from exc

        chunks: List[Chunk] = []
        for chunk_number, chunk_text in enumerate(raw_splits, start=1):
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue

            chunk_id = ChunkIdBuilder.build(
                document_id=page.document_id,
                page_number=page.page_number,
                chunk_number=chunk_number,
            )

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    document_id=page.document_id,
                    file_name=page.file_name,
                    page_start=page.page_number,
                    page_end=page.page_number,
                    chunk_number=chunk_number,
                    text=chunk_text,
                    token_count=self._token_counter.count(chunk_text),
                    metadata={
                        "source": page.file_name,
                        "page": page.page_number,
                        "chunk_number": chunk_number,
                    },
                )
            )

        logger.debug(
            "Page %s of '%s' -> %d chunk(s)",
            page.page_number,
            page.document_id,
            len(chunks),
        )
        return chunks


class DocumentChunker:
    """Top-level entry point: chunks every page of a document independently."""

    def __init__(self, config: ChunkerConfig | None = None) -> None:
        self._config = config or ChunkerConfig()
        self._token_counter = TokenCounter(self._config.tokenizer_model)
        self._page_chunker = PageChunker(self._config, self._token_counter)

    def chunk_pages(self, pages: List[Page]) -> List[Chunk]:
        """Chunk every page in `pages` and return the flattened list of Chunks.

        Each page is processed independently (page-wise, never merged),
        so citations can always be traced back to an exact page number.
        """
        if not pages:
            logger.warning("chunk_pages called with an empty page list")
            return []

        all_chunks: List[Chunk] = []
        for page in pages:
            all_chunks.extend(self._page_chunker.chunk(page))

        logger.info(
            "Chunked %d page(s) into %d chunk(s)", len(pages), len(all_chunks)
        )
        return all_chunks


def chunk_pages(
    pages: List[Page], config: ChunkerConfig | None = None
) -> List[Chunk]:
    """Convenience functional wrapper around DocumentChunker.

    Prefer instantiating DocumentChunker directly when chunking many
    documents in one process, since it avoids reloading the tokenizer
    for every call.
    """
    return DocumentChunker(config).chunk_pages(pages)