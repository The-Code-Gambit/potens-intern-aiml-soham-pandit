class DocumentLoaderError(Exception):
    """Base class for document loading errors."""


class UnsupportedFileTypeError(DocumentLoaderError):
    """Raised when the file extension is unsupported."""


class CorruptedDocumentError(DocumentLoaderError):
    """Raised when a document cannot be read."""


class EmptyDocumentError(DocumentLoaderError):
    """Raised when no text could be extracted."""


class EncryptedDocumentError(DocumentLoaderError):
    """Raised when an encrypted PDF cannot be opened."""
    
    
class ChunkingError(DocumentLoaderError):
    """
    Raised when document chunking fails.
    """
    pass