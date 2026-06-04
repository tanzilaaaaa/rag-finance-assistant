"""
Database Viewer - For showing chunks and embeddings in video recording
This script provides a nice formatted view of your local vector database
"""

import json
import sys
import os

def load_database():
    """Load the local vector database"""
    db_path = "vector_database/chunks.json"
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        print(f"   Expected location: {os.path.abspath(db_path)}")
        print("\n💡 Please upload a PDF first in the Streamlit app")
        return None
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        return chunks
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return None

def display_chunk(chunk, index):
    """Display a single chunk in formatted way"""
    print(f"\n{'='*80}")
    print(f" CHUNK #{index + 1}")
    print(f"{'='*80}")
    
    print(f"\n📌 Chunk ID: {chunk.get('chunk_id', 'N/A')}")
    print(f"📄 Source: {chunk.get('metadata', {}).get('source', 'N/A')}")
    print(f"📖 Page: {chunk.get('metadata', {}).get('page', 'N/A')}")
    print(f"📊 Chunk Index: {chunk.get('metadata', {}).get('chunk_index', 'N/A')}")
    print(f"📏 Size: {chunk.get('metadata', {}).get('chunk_size', 'N/A')} characters")
    print(f"🕐 Created: {chunk.get('created_at', 'N/A')}")
    
    print(f"\n📝 TEXT CONTENT:")
    print(f"{'-'*80}")
    text = chunk.get('text', 'No text')
    # Show first 500 characters
    if len(text) > 500:
        print(text[:500] + "...")
        print(f"\n[... {len(text) - 500} more characters]")
    else:
        print(text)
    
    print(f"\n🔢 EMBEDDING VECTOR:")
    print(f"{'-'*80}")
    embedding = chunk.get('embedding', [])
    if embedding:
        print(f"Dimension: {len(embedding)}")
        print(f"First 20 values: {embedding[:20]}")
        print(f"... (total {len(embedding)} dimensions)")
        print(f"\nSample values:")
        print(f"  Min: {min(embedding):.6f}")
        print(f"  Max: {max(embedding):.6f}")
        print(f"  Mean: {sum(embedding)/len(embedding):.6f}")
    else:
        print("No embedding found")

def display_statistics(chunks):
    """Display database statistics"""
    print(f"\n{'='*80}")
    print(" DATABASE STATISTICS")
    print(f"{'='*80}")
    
    total_chunks = len(chunks)
    sources = set(chunk.get('metadata', {}).get('source', 'unknown') for chunk in chunks)
    total_text_size = sum(len(chunk.get('text', '')) for chunk in chunks)
    avg_chunk_size = total_text_size / total_chunks if total_chunks > 0 else 0
    
    pages = set(chunk.get('metadata', {}).get('page', 0) for chunk in chunks)
    
    print(f"\n📚 Total Chunks: {total_chunks}")
    print(f"📄 Total Pages Covered: {len(pages)}")
    print(f"📖 Unique Sources: {len(sources)}")
    print(f"📏 Average Chunk Size: {avg_chunk_size:.0f} characters")
    print(f"📊 Total Text Size: {total_text_size:,} characters")
    
    print(f"\n📚 Sources:")
    for source in sources:
        count = sum(1 for chunk in chunks if chunk.get('metadata', {}).get('source') == source)
        print(f"  • {source}: {count} chunks")
    
    print(f"\n🔢 Embedding Info:")
    if chunks and chunks[0].get('embedding'):
        embedding_dim = len(chunks[0].get('embedding', []))
        print(f"  • Embedding Dimension: {embedding_dim}")
        print(f"  • Total Embeddings: {total_chunks}")
        print(f"  • Total Vector Values: {total_chunks * embedding_dim:,}")

def main():
    """Main viewer function"""
    print("\n" + "="*80)
    print(" 📊 LOCAL VECTOR DATABASE VIEWER")
    print(" For RAG Investment Analysis System")
    print("="*80)
    
    # Load database
    chunks = load_database()
    
    if not chunks:
        return
    
    # Display statistics
    display_statistics(chunks)
    
    # Ask how many chunks to display
    print(f"\n{'='*80}")
    print(f"Total chunks available: {len(chunks)}")
    
    if len(sys.argv) > 1:
        try:
            num_to_show = int(sys.argv[1])
        except:
            num_to_show = 2
    else:
        num_to_show = 2
    
    print(f"Displaying first {num_to_show} chunks...")
    
    # Display chunks
    for i in range(min(num_to_show, len(chunks))):
        display_chunk(chunks[i], i)
    
    if len(chunks) > num_to_show:
        print(f"\n💡 To see more chunks, run: python view_database.py {len(chunks)}")
    
    print(f"\n{'='*80}")
    print("✅ Database viewer complete!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
