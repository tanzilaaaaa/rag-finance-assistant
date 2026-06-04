"""
Configuration module for RAG system
Loads environment variables and provides configuration constants
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for RAG system"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Firebase Configuration
    FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", "firebase-key.json")
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # Alternative: Use free sentence-transformers if no OpenAI key
    USE_FREE_EMBEDDING = os.getenv("USE_FREE_EMBEDDING", "false").lower() == "true"
    FREE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Retrieval Configuration
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # Firebase Collections
    CHUNKS_COLLECTION = "investment_chunks"
    
    # Application Configuration
    APP_TITLE = os.getenv("APP_TITLE", "RAG Investment Analysis System")
    APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Stock Market & Investment Analysis using RAG")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.USE_FREE_EMBEDDING and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required (or set USE_FREE_EMBEDDING=true)")
        
        if not os.path.exists(cls.FIREBASE_KEY_PATH):
            errors.append(f"Firebase key file not found: {cls.FIREBASE_KEY_PATH}")
        
        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True
    
    @classmethod
    def get_embedding_model_name(cls):
        """Get the appropriate embedding model name"""
        if cls.USE_FREE_EMBEDDING:
            return cls.FREE_EMBEDDING_MODEL
        return cls.EMBEDDING_MODEL
    
    @classmethod
    def display_config(cls):
        """Display current configuration (for debugging)"""
        return {
            "Embedding Model": cls.get_embedding_model_name(),
            "LLM Model": cls.LLM_MODEL,
            "Chunk Size": cls.CHUNK_SIZE,
            "Chunk Overlap": cls.CHUNK_OVERLAP,
            "Top K Results": cls.TOP_K_RESULTS,
            "Similarity Threshold": cls.SIMILARITY_THRESHOLD,
            "Using Free Embeddings": cls.USE_FREE_EMBEDDING
        }
