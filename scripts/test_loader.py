from pathlib import Path

from app.ingest.loader import DocumentLoader

loader = DocumentLoader()

pages = loader.load_document(
    Path("documents/raw/BERT.pdf")
)

print(f"Total pages loaded: {len(pages)}")
print(f"First page number: {pages[0].page_number}")
print("\nPreview:\n")
print(pages[0].text[:500])