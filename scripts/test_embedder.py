"""
Integration test for the embedding pipeline.

Pipeline:
    Loader
        ↓
    Cleaner
        ↓
    Chunker
        ↓
    Embedder
"""

from pathlib import Path

from app.ingest.loader import DocumentLoader
from app.ingest.cleaner import TextCleaner
from app.ingest.chunker import DocumentChunker
from app.ingest.embedder import Embedder


def main() -> None:
    pdf_path = Path("documents/raw/attention.pdf")

    print("=" * 80)
    print("Loading document...")
    print("=" * 80)

    loader = DocumentLoader()
    pages = loader.load_document(pdf_path)

    print(f"Pages loaded: {len(pages)}")

    print("\nCleaning pages...")
    cleaner = TextCleaner()
    pages = cleaner.clean_pages(pages)

    print("Chunking pages...")
    chunker = DocumentChunker()
    chunks = chunker.chunk_pages(pages)

    print(f"Chunks created: {len(chunks)}")

    print("\nGenerating embeddings...")
    embedder = Embedder()
    chunks = embedder.embed_chunks(chunks)

    embedded_chunks = [c for c in chunks if c.embedding is not None]

    print("\n" + "=" * 80)
    print("Embedding Statistics")
    print("=" * 80)

    print(f"Embedding model : {embedder._config.model_name}")
    print(f"Device          : {embedder.device}")
    print(f"Chunks embedded : {len(embedded_chunks)}")
    print(f"Skipped chunks  : {len(chunks) - len(embedded_chunks)}")

    if embedded_chunks:
        first = embedded_chunks[0]

        print("\nFirst Chunk")
        print("-" * 80)
        print(f"Chunk ID      : {first.chunk_id}")
        print(f"Source        : {first.file_name}")
        print(f"Page          : {first.page_start}")
        print(f"Token Count   : {first.token_count}")
        print(f"Vector Length : {len(first.embedding)}")

        print("\nFirst 10 embedding values")
        print(first.embedding[:10])

        print("\nChunk Preview")
        print("-" * 80)
        print(first.text[:400])

    print("\nTesting query embedding...")

    query = "What is self-attention?"

    query_embedding = embedder.embed_query(query)

    print(f'Query: "{query}"')
    print(f"Query vector length: {len(query_embedding)}")
    print(f"First 10 values: {query_embedding[:10]}")

    print("\nAll tests completed successfully.")


if __name__ == "__main__":
    main()