"""
RAG Investment Analysis System
Source package initialization
"""

from .config import Config
from .pdf_processor import PDFProcessor
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .retriever import SemanticRetriever
from .llm_handler import LLMHandler

__version__ = "1.0.0"
__author__ = "Student"
__description__ = "RAG system for investment analysis"

__all__ = [
    'Config',
    'PDFProcessor',
    'EmbeddingGenerator',
    'VectorStore',
    'SemanticRetriever',
    'LLMHandler'
]
