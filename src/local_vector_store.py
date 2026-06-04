"""
Local Vector Store Module
Handles local JSON-based storage for chunks and embeddings (Firebase alternative)
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class LocalVectorStore:
    """Manage vector storage using local JSON files"""
    
    def __init__(self, storage_dir: str = "vector_database"):
        """
        Initialize local vector store
        
        Args:
            storage_dir: Directory to store JSON files
        """
        self.storage_dir = storage_dir
        self.chunks_file = os.path.join(storage_dir, "chunks.json")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        
        # Create storage directory if it doesn't exist
        Path(storage_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize empty database if files don't exist
        if not os.path.exists(self.chunks_file):
            self._save_chunks([])
        
        if not os.path.exists(self.metadata_file):
            self._save_metadata({
                "created_at": datetime.now().isoformat(),
                "total_chunks": 0,
                "sources": []
            })
        
        print(f"Local vector store initialized at: {self.storage_dir}")
    
    def _load_chunks(self) -> List[Dict]:
        """Load all chunks from JSON file"""
        try:
            with open(self.chunks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chunks: {e}")
            return []
    
    def _save_chunks(self, chunks: List[Dict]):
        """Save chunks to JSON file"""
        try:
            with open(self.chunks_file, 'w', encoding='utf-8') as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chunks: {e}")
    
    def _load_metadata(self) -> Dict:
        """Load metadata from JSON file"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return {}
    
    def _save_metadata(self, metadata: Dict):
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def store_chunk(self, chunk_data: Dict) -> str:
        """
        Store a single chunk with embedding
        
        Args:
            chunk_data: Dictionary containing chunk_id, text, embedding, and metadata
            
        Returns:
            Chunk ID
        """
        try:
            chunks = self._load_chunks()
            
            # Add timestamp
            chunk_data['created_at'] = datetime.now().isoformat()
            
            # Check if chunk already exists and update, otherwise append
            existing_index = None
            for i, chunk in enumerate(chunks):
                if chunk.get('chunk_id') == chunk_data['chunk_id']:
                    existing_index = i
                    break
            
            if existing_index is not None:
                chunks[existing_index] = chunk_data
            else:
                chunks.append(chunk_data)
            
            self._save_chunks(chunks)
            self._update_metadata()
            
            return chunk_data['chunk_id']
        
        except Exception as e:
            print(f"Error storing chunk {chunk_data.get('chunk_id')}: {e}")
            raise
    
    def store_chunks_batch(self, chunks_data: List[Dict], batch_size: int = 500) -> int:
        """
        Store multiple chunks in batches
        
        Args:
            chunks_data: List of chunk dictionaries
            batch_size: Number of chunks per batch (for consistency with Firebase)
            
        Returns:
            Number of chunks stored
        """
        try:
            existing_chunks = self._load_chunks()
            
            # Add timestamps
            for chunk in chunks_data:
                chunk['created_at'] = datetime.now().isoformat()
            
            # Append new chunks
            existing_chunks.extend(chunks_data)
            
            self._save_chunks(existing_chunks)
            self._update_metadata()
            
            print(f"Successfully stored {len(chunks_data)} chunks")
            return len(chunks_data)
        
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
            chunks = self._load_chunks()
            
            for chunk in chunks:
                if chunk.get('chunk_id') == chunk_id:
                    return chunk
            
            return None
        
        except Exception as e:
            print(f"Error retrieving chunk {chunk_id}: {e}")
            return None
    
    def get_all_chunks(self, limit: int = None) -> List[Dict]:
        """
        Retrieve all chunks
        
        Args:
            limit: Maximum number of chunks to retrieve
            
        Returns:
            List of chunk dictionaries
        """
        try:
            chunks = self._load_chunks()
            
            if limit:
                return chunks[:limit]
            
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
            chunks = self._load_chunks()
            
            filtered_chunks = [
                chunk for chunk in chunks
                if chunk.get('metadata', {}).get('source') == source_name
            ]
            
            return filtered_chunks
        
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
            chunks = self._load_chunks()
            
            filtered_chunks = [
                chunk for chunk in chunks
                if chunk.get('chunk_id') != chunk_id
            ]
            
            self._save_chunks(filtered_chunks)
            self._update_metadata()
            
            return True
        
        except Exception as e:
            print(f"Error deleting chunk {chunk_id}: {e}")
            return False
    
    def delete_all_chunks(self) -> int:
        """
        Delete all chunks
        WARNING: This is irreversible!
        
        Returns:
            Number of chunks deleted
        """
        try:
            chunks = self._load_chunks()
            deleted_count = len(chunks)
            
            self._save_chunks([])
            self._update_metadata()
            
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
            chunks = self._load_chunks()
            
            filtered_chunks = [
                chunk for chunk in chunks
                if chunk.get('metadata', {}).get('source') != source_name
            ]
            
            deleted_count = len(chunks) - len(filtered_chunks)
            
            self._save_chunks(filtered_chunks)
            self._update_metadata()
            
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
            chunks = self._load_chunks()
            
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
                'avg_chunk_size': total_size / len(chunks) if chunks else 0,
                'storage_location': os.path.abspath(self.storage_dir)
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
            chunks = self._load_chunks()
            
            # Filter chunks containing the search text
            matching_chunks = [
                chunk for chunk in chunks 
                if search_text.lower() in chunk.get('text', '').lower()
            ]
            
            return matching_chunks[:limit]
        
        except Exception as e:
            print(f"Error searching text: {e}")
            return []
    
    def _update_metadata(self):
        """Update metadata file with current statistics"""
        try:
            stats = self.get_collection_stats()
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'total_chunks': stats.get('total_chunks', 0),
                'sources': stats.get('sources', []),
                'source_counts': stats.get('source_counts', {}),
                'storage_location': stats.get('storage_location', '')
            }
            self._save_metadata(metadata)
        except Exception as e:
            print(f"Error updating metadata: {e}")
    
    def export_to_json(self, output_file: str):
        """
        Export all data to a single JSON file
        
        Args:
            output_file: Path to output JSON file
        """
        try:
            chunks = self._load_chunks()
            metadata = self._load_metadata()
            
            export_data = {
                'metadata': metadata,
                'chunks': chunks
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"Exported {len(chunks)} chunks to {output_file}")
        
        except Exception as e:
            print(f"Error exporting data: {e}")


# Test function
if __name__ == "__main__":
    print("Local Vector Store module - test mode")
    store = LocalVectorStore()
    print(f"Storage location: {store.storage_dir}")
    print(f"Stats: {store.get_collection_stats()}")
