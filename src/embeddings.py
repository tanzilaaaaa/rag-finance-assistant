"""
Embeddings Module
Handles vector embedding generation using OpenAI or Sentence Transformers
"""

from typing import List, Union
import numpy as np
from config import Config


class EmbeddingGenerator:
    """Generate embeddings for text chunks"""
    
    def __init__(self, use_openai: bool = None):
        """
        Initialize embedding generator
        
        Args:
            use_openai: Whether to use OpenAI (if None, uses Config setting)
        """
        if use_openai is None:
            self.use_openai = not Config.USE_FREE_EMBEDDING
        else:
            self.use_openai = use_openai
        
        self.model_name = Config.get_embedding_model_name()
        
        if self.use_openai:
            self._init_openai()
        else:
            self._init_sentence_transformer()
    
    def _init_openai(self):
        """Initialize OpenAI embeddings"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.embedding_dim = 1536  # Default for OpenAI embeddings
            print(f"Initialized OpenAI embeddings: {self.model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI: {e}")
    
    def _init_sentence_transformer(self):
        """Initialize Sentence Transformer embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"Initialized Sentence Transformer: {self.model_name}")
            print(f"Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Sentence Transformer: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.use_openai:
            return self._generate_openai_embedding(text)
        else:
            return self._generate_sentence_transformer_embedding(text)
    
    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating OpenAI embedding: {e}")
            raise
    
    def _generate_sentence_transformer_embedding(self, text: str) -> List[float]:
        """Generate embedding using Sentence Transformer"""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating Sentence Transformer embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if self.use_openai:
            return self._generate_openai_embeddings_batch(texts)
        else:
            return self._generate_sentence_transformer_embeddings_batch(texts, batch_size)
    
    def _generate_openai_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings in batch using OpenAI API"""
        embeddings = []
        
        # OpenAI API has input limits, process in smaller batches
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"Error in batch {i//batch_size}: {e}")
                # Fallback to individual processing
                for text in batch:
                    embeddings.append(self.generate_embedding(text))
        
        return embeddings
    
    def _generate_sentence_transformer_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int
    ) -> List[List[float]]:
        """Generate embeddings in batch using Sentence Transformer"""
        try:
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating batch embeddings: {e}")
            # Fallback to individual processing
            return [self.generate_embedding(text) for text in texts]
    
    def cosine_similarity(
        self, 
        embedding1: Union[List[float], np.ndarray],
        embedding2: Union[List[float], np.ndarray]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    def get_embedding_info(self) -> dict:
        """Get information about the embedding model"""
        return {
            'model_name': self.model_name,
            'use_openai': self.use_openai,
            'embedding_dimension': self.embedding_dim,
            'backend': 'OpenAI' if self.use_openai else 'Sentence Transformers'
        }


# Test function
if __name__ == "__main__":
    # Test with free model
    print("Testing Sentence Transformer...")
    generator = EmbeddingGenerator(use_openai=False)
    
    test_text = "This is a test sentence about stock market investing."
    embedding = generator.generate_embedding(test_text)
    
    print(f"Generated embedding of dimension: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
    print(f"Model info: {generator.get_embedding_info()}")
