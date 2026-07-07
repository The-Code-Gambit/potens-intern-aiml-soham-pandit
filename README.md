# Potens AI/ML Internship Assignment
### Document Question Answering with Citations (RAG System)

## Overview

This repository contains my submission for the Potens AI/ML Internship Take-Home Assignment.

The goal of this project is to build a production-oriented Retrieval-Augmented Generation (RAG) system capable of:

- Ingesting PDF and text documents
- Creating semantic chunks
- Generating dense vector embeddings
- Indexing embeddings into a vector database
- Performing semantic retrieval
- Answering user questions with citations
- Detecting contradictions across documents
- Supporting multilingual queries

The implementation emphasizes clean software architecture, modularity, maintainability, and production-ready engineering practices.

---

# Current Progress

## ✅ Completed

### Project Architecture

- Modular project structure
- Separation of concerns
- SOLID-oriented design
- Structured logging
- Custom exception hierarchy
- Type hints and dataclasses

---

### Document Ingestion Pipeline

Implemented a robust document ingestion pipeline supporting:

- PDF loading using PyMuPDF
- TXT document loading
- SHA256-based document IDs
- Page-wise extraction
- Corrupted document detection
- Encrypted PDF detection
- Empty document validation
- File type validation

Output:

```
Document
    ↓
List[Page]
```

---

### Text Cleaning Pipeline

Implemented a dedicated preprocessing module performing:

- Unicode normalization
- Whitespace cleanup
- Hyphenated word repair
- Paragraph normalization
- Preservation of original page text

Output:

```
List[Page]
    ↓
Cleaned Pages
```

---

### Semantic Chunking Pipeline

Implemented a production-oriented chunking module using:

- LangChain RecursiveCharacterTextSplitter
- Page-wise chunking
- Token counting with BAAI tokenizer
- Deterministic SHA256 chunk IDs
- Rich metadata generation
- Configurable chunk size and overlap

Each chunk preserves:

- Document ID
- File name
- Page number
- Chunk number
- Token count
- Metadata

Output:

```
Cleaned Pages
    ↓
List[Chunk]
```

---

### Embedding Pipeline

Implemented an embedding module using:

Sentence Transformers

Model:

```
BAAI/bge-small-en-v1.5
```

Features:

- Batch embedding
- Query embedding
- Automatic CPU/GPU detection
- Normalized embeddings
- Batch logging
- Exception handling

Each Chunk is enriched with its embedding vector.

Output:

```
Chunks
    ↓
Embedded Chunks
```

---

### Testing

Implemented standalone integration tests for:

- Loader
- Cleaner
- Chunker
- Embedder

allowing each stage of the pipeline to be independently validated.

---

# Project Structure

```
app/

│
├── api/
│
├── core/
│   ├── logger.py
│
├── ingest/
│   ├── loader.py
│   ├── cleaner.py
│   ├── chunker.py
│   ├── models.py
│   └── exceptions.py
│
├── embedding/
│   └── embedder.py
│
├── retrieval/
│
├── ui/
│
└── utils/

documents/
scripts/
tests/
```

---

# Current Pipeline

```
PDF / TXT
        │
        ▼
Document Loader
        │
        ▼
Text Cleaner
        │
        ▼
Semantic Chunker
        │
        ▼
Embedding Generator
```

---

# Technologies Used

- Python 3.11
- PyMuPDF
- Sentence Transformers
- LangChain Text Splitters
- HuggingFace Transformers
- NumPy
- Logging
- Dataclasses
- Type Hints

---

# Features Implemented

- Robust document ingestion
- Semantic chunking
- Token-aware processing
- Deterministic chunk IDs
- Batch embedding
- Query embedding
- Modular architecture
- Production-style logging
- Strong exception handling
- Integration test scripts

---

# Remaining Work

The following modules were planned but not completed within the submission window:

### Vector Database

- ChromaDB integration
- Persistent vector storage
- Metadata indexing
- Similarity search

---

### Retrieval Pipeline

- Semantic search
- Top-K retrieval
- Similarity score calculation

---

### Question Answering

- Gemini API integration
- Prompt engineering
- Context assembly
- Citation generation

---

### Contradiction Detection

- Cross-document comparison
- Evidence extraction
- Conflict classification

---

### Multilingual Support

- Query translation
- Response translation

---

### User Interface

- Streamlit frontend
- Upload interface
- Chat interface
- Citation display

---

### REST API

- FastAPI endpoints
- Document upload
- Question answering
- Retrieval APIs

---

# Engineering Decisions

Some important design choices made during implementation:

- Page-wise chunking to preserve accurate citations.
- Recursive semantic chunking using LangChain Text Splitters.
- Deterministic SHA256 chunk identifiers for idempotent indexing.
- SentenceTransformer used directly instead of LangChain embedding wrappers.
- Strong separation between ingestion, embedding, retrieval, and future QA modules.
- Batch embedding for improved performance.
- Clean object-oriented architecture with independent, testable components.

---

# Future Work

Future development will complete the full RAG pipeline by implementing:

```
Document
      │
      ▼
Loader
      │
      ▼
Cleaner
      │
      ▼
Chunker
      │
      ▼
Embedder
      │
      ▼
ChromaDB
      │
      ▼
Retriever
      │
      ▼
Gemini
      │
      ▼
Answer + Citations
```

along with contradiction detection, multilingual support, FastAPI backend, and Streamlit frontend.

---

# Author

**Soham Pandit**

Bachelor of Engineering (Electronics & Computer Engineering)

Potens AI/ML Internship Assignment