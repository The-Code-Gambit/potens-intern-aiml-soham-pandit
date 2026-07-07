from pathlib import Path

from app.ingest.cleaner import TextCleaner
from app.ingest.loader import DocumentLoader

loader = DocumentLoader()
cleaner = TextCleaner()

pages = loader.load_document(
    Path("documents/raw/LoRA.pdf")
)

pages = cleaner.clean_pages(pages)

print("=" * 80)
print("RAW")
print("=" * 80)

print(pages[0].text[:800])

print()

print("=" * 80)
print("CLEANED")
print("=" * 80)

print(pages[0].cleaned_text[:800])