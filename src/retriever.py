"""
Retriever Module
Handles semantic search and retrieval of relevant chunks
"""

from typing import List, Dict, Tuple
import numpy as np
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from config import Config


class SemanticRetriever:
    """Perform semantic search over stored chunks"""
    
    def __init__(
        self, 
        vector_store: VectorStore,
        embedding_generator: EmbeddingGenerator,
        top_k: int = None,
        similarity_threshold: float = None
    ):
        """
        Initialize retriever
        
        Args:
            vector_store: Vector store instance
            embedding_generator: Embedding generator instance
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.top_k = top_k or Config.TOP_K_RESULTS
        self.similarity_threshold = similarity_threshold or Config.SIMILARITY_THRESHOLD
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = None,
        filter_source: str = None
    ) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query
        
        Args:
            query: Search query
            top_k: Number of results (overrides default)
            filter_source: Optional source name to filter by
            
        Returns:
            List of chunks with similarity scores
        """
        k = top_k or self.top_k
        
        # Generate query embedding
        print(f"Generating embedding for query: {query[:50]}...")
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Get all chunks from vector store
        print("Retrieving chunks from vector store...")
        if filter_source:
            chunks = self.vector_store.get_chunks_by_source(filter_source)
        else:
            chunks = self.vector_store.get_all_chunks()
        
        if not chunks:
            print("No chunks found in vector store")
            return []
        
        print(f"Found {len(chunks)} chunks, calculating similarities...")
        
        # Calculate similarities
        similarities = []
        for chunk in chunks:
            chunk_embedding = chunk.get('embedding', [])
            
            if not chunk_embedding:
                continue
            
            # Calculate cosine similarity
            similarity = self.embedding_generator.cosine_similarity(
                query_embedding,
                chunk_embedding
            )
            
            similarities.append((chunk, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold and get top k
        filtered_results = [
            {
                'chunk': chunk,
                'similarity': score,
                'text': chunk.get('text', ''),
                'metadata': chunk.get('metadata', {}),
                'chunk_id': chunk.get('chunk_id', '')
            }
            for chunk, score in similarities
            if score >= self.similarity_threshold
        ][:k]
        
        print(f"Returning {len(filtered_results)} results above threshold {self.similarity_threshold}")
        
        return filtered_results
    
    def retrieve_with_reranking(
        self,
        query: str,
        initial_k: int = 20,
        final_k: int = None
    ) -> List[Dict]:
        """
        Retrieve with two-stage retrieval and reranking
        
        Args:
            query: Search query
            initial_k: Number of candidates in first stage
            final_k: Final number of results
            
        Returns:
            List of reranked chunks
        """
        final_k = final_k or self.top_k
        
        # First stage: retrieve more candidates
        candidates = self.retrieve(query, top_k=initial_k)
        
        if not candidates:
            return []
        
        # Second stage: rerank based on exact keyword matching
        # (simple reranking, can be enhanced with cross-encoder models)
        query_terms = set(query.lower().split())
        
        for candidate in candidates:
            text_terms = set(candidate['text'].lower().split())
            keyword_overlap = len(query_terms & text_terms)
            
            # Combine similarity score with keyword overlap
            candidate['rerank_score'] = (
                candidate['similarity'] * 0.7 + 
                (keyword_overlap / len(query_terms)) * 0.3
            )
        
        # Sort by rerank score
        candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return candidates[:final_k]
    
    def retrieve_by_keywords(
        self,
        keywords: List[str],
        top_k: int = None
    ) -> List[Dict]:
        """
        Retrieve chunks containing specific keywords
        
        Args:
            keywords: List of keywords to search for
            top_k: Number of results
            
        Returns:
            List of matching chunks
        """
        k = top_k or self.top_k
        chunks = self.vector_store.get_all_chunks()
        
        matching_chunks = []
        
        for chunk in chunks:
            text = chunk.get('text', '').lower()
            
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword.lower() in text)
            
            if matches > 0:
                matching_chunks.append({
                    'chunk': chunk,
                    'text': chunk.get('text', ''),
                    'metadata': chunk.get('metadata', {}),
                    'chunk_id': chunk.get('chunk_id', ''),
                    'keyword_matches': matches
                })
        
        # Sort by number of matches
        matching_chunks.sort(key=lambda x: x['keyword_matches'], reverse=True)
        
        return matching_chunks[:k]
    
    def format_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context string for LLM
        
        Args:
            retrieved_chunks: List of retrieved chunk dictionaries
            
        Returns:
            Formatted context string
        """
        if not retrieved_chunks:
            return "No relevant context found."
        
        context_parts = []
        
        for i, item in enumerate(retrieved_chunks, 1):
            text = item.get('text', '')
            metadata = item.get('metadata', {})
            similarity = item.get('similarity', 0)
            
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', 'unknown')
            
            context_parts.append(
                f"[Context {i}] (Source: {source}, Page: {page}, Relevance: {similarity:.3f})\n{text}"
            )
        
        return "\n\n".join(context_parts)
    
    def get_retrieval_stats(self, retrieved_chunks: List[Dict]) -> Dict:
        """
        Get statistics about retrieved chunks
        
        Args:
            retrieved_chunks: List of retrieved chunks
            
        Returns:
            Dictionary with statistics
        """
        if not retrieved_chunks:
            return {}
        
        similarities = [item.get('similarity', 0) for item in retrieved_chunks]
        sources = [item.get('metadata', {}).get('source', 'unknown') for item in retrieved_chunks]
        pages = [item.get('metadata', {}).get('page', 0) for item in retrieved_chunks]
        
        return {
            'num_results': len(retrieved_chunks),
            'avg_similarity': np.mean(similarities),
            'max_similarity': max(similarities),
            'min_similarity': min(similarities),
            'unique_sources': len(set(sources)),
            'unique_pages': len(set(pages)),
            'sources': list(set(sources))
        }


# Test function
if __name__ == "__main__":
    print("Semantic Retriever module - test mode")
    print(f"Default top_k: {Config.TOP_K_RESULTS}")
    print(f"Default threshold: {Config.SIMILARITY_THRESHOLD}")
