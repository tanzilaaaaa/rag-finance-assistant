"""
Vector Store Module
Handles Firebase Firestore operations for storing and retrieving chunks with embeddings
"""

from typing import List, Dict, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from config import Config


class VectorStore:
    """Manage vector storage in Firebase Firestore"""
    
    def __init__(self, firebase_key_path: str = None):
        """
        Initialize Firebase connection
        
        Args:
            firebase_key_path: Path to Firebase service account key
        """
        self.firebase_key_path = firebase_key_path or Config.FIREBASE_KEY_PATH
        self.collection_name = Config.CHUNKS_COLLECTION
        
        # Initialize Firebase app if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.firebase_key_path)
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully")
        
        # Get Firestore client
        self.db = firestore.client()
        self.collection = self.db.collection(self.collection_name)
        print(f"Connected to Firestore collection: {self.collection_name}")
    
    def store_chunk(self, chunk_data: Dict) -> str:
        """
        Store a single chunk with embedding in Firestore
        
        Args:
            chunk_data: Dictionary containing chunk_id, text, embedding, and metadata
            
        Returns:
            Document ID
        """
        try:
            # Prepare document data
            doc_data = {
                'chunk_id': chunk_data['chunk_id'],
                'text': chunk_data['text'],
                'embedding': chunk_data['embedding'],
                'metadata': chunk_data.get('metadata', {}),
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            # Store in Firestore
            doc_ref = self.collection.document(chunk_data['chunk_id'])
            doc_ref.set(doc_data)
            
            return chunk_data['chunk_id']
        
        except Exception as e:
            print(f"Error storing chunk {chunk_data.get('chunk_id')}: {e}")
            raise
    
    def store_chunks_batch(self, chunks_data: List[Dict], batch_size: int = 500) -> int:
        """
        Store multiple chunks in batches
        
        Args:
            chunks_data: List of chunk dictionaries
            batch_size: Number of documents per batch (Firestore limit is 500)
            
        Returns:
            Number of chunks stored
        """
        stored_count = 0
        
        try:
            # Process in batches
            for i in range(0, len(chunks_data), batch_size):
                batch = self.db.batch()
                batch_chunks = chunks_data[i:i + batch_size]
                
                for chunk_data in batch_chunks:
                    doc_data = {
                        'chunk_id': chunk_data['chunk_id'],
                        'text': chunk_data['text'],
                        'embedding': chunk_data['embedding'],
                        'metadata': chunk_data.get('metadata', {}),
                        'created_at': firestore.SERVER_TIMESTAMP
                    }
                    
                    doc_ref = self.collection.document(chunk_data['chunk_id'])
                    batch.set(doc_ref, doc_data)
                
                # Commit batch
                batch.commit()
                stored_count += len(batch_chunks)
                print(f"Stored batch {i//batch_size + 1}: {stored_count}/{len(chunks_data)} chunks")
            
            print(f"Successfully stored {stored_count} chunks")
            return stored_count
        
        except Exception as e:
            print(f"Error storing chunks in batch: {e}")
            raise
    
    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """
        Retrieve a single chunk by ID
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            Chunk data dictionary or None if not found
        """
        try:
            doc_ref = self.collection.document(chunk_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        
        except Exception as e:
            print(f"Error retrieving chunk {chunk_id}: {e}")
            return None
    
    def get_all_chunks(self, limit: int = None) -> List[Dict]:
        """
        Retrieve all chunks from Firestore
        
        Args:
            limit: Maximum number of chunks to retrieve
            
        Returns:
            List of chunk dictionaries
        """
        try:
            query = self.collection
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            chunks = [doc.to_dict() for doc in docs]
            
            return chunks
        
        except Exception as e:
            print(f"Error retrieving all chunks: {e}")
            return []
    
    def get_chunks_by_source(self, source_name: str) -> List[Dict]:
        """
        Retrieve chunks from a specific source
        
        Args:
            source_name: Name of the source document
            
        Returns:
            List of chunk dictionaries
        """
        try:
            query = self.collection.where('metadata.source', '==', source_name)
            docs = query.stream()
            chunks = [doc.to_dict() for doc in docs]
            
            return chunks
        
        except Exception as e:
            print(f"Error retrieving chunks for source {source_name}: {e}")
            return []
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a single chunk
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            True if successful
        """
        try:
            self.collection.document(chunk_id).delete()
            return True
        
        except Exception as e:
            print(f"Error deleting chunk {chunk_id}: {e}")
            return False
    
    def delete_all_chunks(self) -> int:
        """
        Delete all chunks from the collection
        WARNING: This is irreversible!
        
        Returns:
            Number of chunks deleted
        """
        try:
            deleted_count = 0
            batch_size = 500
            
            # Get all documents
            docs = self.collection.limit(batch_size).stream()
            deleted = 0
            
            for doc in docs:
                doc.reference.delete()
                deleted += 1
                deleted_count += 1
            
            # Continue until no more documents
            while deleted >= batch_size:
                docs = self.collection.limit(batch_size).stream()
                deleted = 0
                
                for doc in docs:
                    doc.reference.delete()
                    deleted += 1
                    deleted_count += 1
            
            print(f"Deleted {deleted_count} chunks")
            return deleted_count
        
        except Exception as e:
            print(f"Error deleting all chunks: {e}")
            return 0
    
    def delete_chunks_by_source(self, source_name: str) -> int:
        """
        Delete all chunks from a specific source
        
        Args:
            source_name: Name of the source document
            
        Returns:
            Number of chunks deleted
        """
        try:
            query = self.collection.where('metadata.source', '==', source_name)
            docs = query.stream()
            
            deleted_count = 0
            batch = self.db.batch()
            
            for doc in docs:
                batch.delete(doc.reference)
                deleted_count += 1
            
            batch.commit()
            print(f"Deleted {deleted_count} chunks from source {source_name}")
            
            return deleted_count
        
        except Exception as e:
            print(f"Error deleting chunks for source {source_name}: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            chunks = self.get_all_chunks()
            
            if not chunks:
                return {
                    'total_chunks': 0,
                    'sources': [],
                    'total_size': 0
                }
            
            # Calculate statistics
            sources = set(chunk['metadata'].get('source', 'unknown') for chunk in chunks)
            total_size = sum(len(chunk.get('text', '')) for chunk in chunks)
            
            source_counts = {}
            for chunk in chunks:
                source = chunk['metadata'].get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            return {
                'total_chunks': len(chunks),
                'sources': list(sources),
                'source_counts': source_counts,
                'total_size': total_size,
                'avg_chunk_size': total_size / len(chunks) if chunks else 0
            }
        
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {}
    
    def search_by_text(self, search_text: str, limit: int = 10) -> List[Dict]:
        """
        Simple text search in chunks (not semantic)
        
        Args:
            search_text: Text to search for
            limit: Maximum results
            
        Returns:
            List of matching chunks
        """
        try:
            chunks = self.get_all_chunks()
            
            # Filter chunks containing the search text
            matching_chunks = [
                chunk for chunk in chunks 
                if search_text.lower() in chunk.get('text', '').lower()
            ]
            
            return matching_chunks[:limit]
        
        except Exception as e:
            print(f"Error searching text: {e}")
            return []


# Test function
if __name__ == "__main__":
    print("Vector Store module - test mode")
    print(f"Collection name: {Config.CHUNKS_COLLECTION}")
