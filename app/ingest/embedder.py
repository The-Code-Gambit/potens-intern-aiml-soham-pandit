"""
Embedding Pipeline

Single responsibility: convert text into dense vector embeddings using
a local Sentence Transformers model.

This module intentionally knows nothing about:
    - ChromaDB or any vector store
    - Retrieval / similarity search
    - Gemini or any LLM

It exposes exactly two operations:
    - embed_chunks(chunks)  -> batch embeds Chunk.text, mutates Chunk.embedding
    - embed_query(text)     -> embeds a single query string at retrieval time

Both are backed by the same underlying SentenceTransformer instance, so
chunk embeddings and query embeddings always live in the same vector
space.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from sentence_transformers import SentenceTransformer

from app.core.logger import get_logger
from app.ingest.exceptions import EmbeddingError
from app.ingest.models import Chunk

logger = get_logger(__name__)

DEFAULT_MODEL_NAME = "BAAI/bge-small-en-v1.5"


@dataclass(frozen=True)
class EmbedderConfig:
    """Immutable configuration for the Embedder.

    Attributes:
        model_name: Sentence Transformers model identifier to load.
        batch_size: Number of texts encoded per forward pass.
        device: Torch device string ("cuda", "mps", "cpu"). If None,
            the best available device is auto-detected.
        normalize_embeddings: Whether to L2-normalize output vectors.
            Required for cosine-similarity search to behave correctly
            in Chroma, and keeps output magnitude-independent, which
            keeps embeddings deterministic across runs.
        show_progress_bar: Whether SentenceTransformer prints its own
            tqdm progress bar. Kept False by default; we log batch
            progress ourselves instead (no print()).
    """

    model_name: str = DEFAULT_MODEL_NAME
    batch_size: int = 32
    device: Optional[str] = None
    normalize_embeddings: bool = True
    show_progress_bar: bool = False


def _resolve_device(requested_device: Optional[str]) -> str:
    """Resolve the compute device to run embeddings on.

    Parameters:
        requested_device: An explicit device string, or None to
            auto-detect.

    Returns:
        A valid torch device string: "cuda", "mps", or "cpu".

    Raises:
        Never raises. Falls back to "cpu" if detection fails for any
        reason, since embedding must remain usable on any machine.
    """
    if requested_device:
        return requested_device

    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():  # Apple Silicon
            return "mps"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Device auto-detection failed, defaulting to CPU: %s", exc)

    return "cpu"


class Embedder:
    """Encodes text into dense vector embeddings.

    The model is loaded once at construction time and reused for both
    batch chunk embedding and single-query embedding, guaranteeing
    both live in the same vector space.
    """

    def __init__(self, config: Optional[EmbedderConfig] = None) -> None:
        """Load the embedding model.

        Parameters:
            config: Embedder configuration. Defaults to
                EmbedderConfig() (BGE-small, auto device).

        Raises:
            EmbeddingError: If the model fails to load.
        """
        self._config = config or EmbedderConfig()
        device = _resolve_device(self._config.device)

        logger.info(
            "Loading embedding model '%s' on device '%s'",
            self._config.model_name,
            device,
        )

        try:
            self._model = SentenceTransformer(self._config.model_name, device=device)
        except Exception as exc:  # noqa: BLE001
            raise EmbeddingError(
                f"Failed to load embedding model '{self._config.model_name}': {exc}"
            ) from exc

        self._device = device

    @property
    def device(self) -> str:
        """Return the compute device the model is running on."""
        return self._device

    def embed_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Embed a batch of chunks and populate Chunk.embedding in place.

        Parameters:
            chunks: Chunks to embed. Chunks with empty text are skipped
                (left with embedding=None) rather than sent to the model.

        Returns:
            The same list of Chunk objects, with `.embedding` populated
            for every chunk that had non-empty text.

        Raises:
            EmbeddingError: If the underlying model fails to encode
                the batch.
        """
        if not chunks:
            logger.warning("embed_chunks called with an empty chunk list")
            return chunks

        embeddable = [c for c in chunks if c.text and c.text.strip()]
        skipped = len(chunks) - len(embeddable)
        if skipped:
            logger.warning("Skipping %d chunk(s) with empty text", skipped)

        if not embeddable:
            return chunks

        texts = [c.text for c in embeddable]

        logger.info(
            "Embedding %d chunk(s) in batches of %d on '%s'",
            len(texts),
            self._config.batch_size,
            self._device,
        )

        start = time.perf_counter()
        try:
            vectors = self._model.encode(
                texts,
                batch_size=self._config.batch_size,
                show_progress_bar=self._config.show_progress_bar,
                normalize_embeddings=self._config.normalize_embeddings,
                convert_to_numpy=True,
            )
        except Exception as exc:  # noqa: BLE001
            raise EmbeddingError(
                f"Failed to embed batch of {len(texts)} chunk(s): {exc}"
            ) from exc

        elapsed = time.perf_counter() - start
        logger.info(
            "Embedded %d chunk(s) in %.2fs (%.1f chunks/sec)",
            len(texts),
            elapsed,
            len(texts) / elapsed if elapsed > 0 else float("inf"),
        )

        for chunk, vector in zip(embeddable, vectors):
            chunk.embedding = vector.tolist()

        return chunks

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string, for use at retrieval time.

        Parameters:
            text: The user's question or search string.

        Returns:
            A dense embedding vector as a list of floats, in the same
            vector space as embed_chunks() output.

        Raises:
            EmbeddingError: If `text` is empty, or if encoding fails.
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed an empty query string")

        try:
            vector = self._model.encode(
                text,
                normalize_embeddings=self._config.normalize_embeddings,
                convert_to_numpy=True,
            )
        except Exception as exc:  # noqa: BLE001
            raise EmbeddingError(f"Failed to embed query: {exc}") from exc

        return vector.tolist()