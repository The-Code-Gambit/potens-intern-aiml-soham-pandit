from pathlib import Path

from app.ingest.loader import DocumentLoader
from app.ingest.cleaner import TextCleaner
from app.ingest.chunker import DocumentChunker

loader = DocumentLoader()
cleaner = TextCleaner()
chunker = DocumentChunker()

pdf_path = Path("documents/raw/Gemini Technical Report.pdf")

print(f"Loading document: {pdf_path}")

pages = loader.load_document(pdf_path)

print(f"Pages loaded: {len(pages)}")

pages = cleaner.clean_pages(pages)

chunks = chunker.chunk_pages(pages)

print("=" * 80)
print(f"Total chunks: {len(chunks)}")
print("=" * 80)

for chunk in chunks[:3]:
    print(f"\nChunk #{chunk.chunk_number}")
    print(f"Page: {chunk.page_start}")
    print(f"Tokens: {chunk.token_count}")
    print("-" * 50)
    print(chunk.text[:300])