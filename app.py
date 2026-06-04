"""
RAG Investment Analysis System - Streamlit Application
Main application interface for PDF upload and querying
"""

import streamlit as st
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from pdf_processor import PDFProcessor
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from retriever import SemanticRetriever
from llm_handler import LLMHandler


# Page configuration
st.set_page_config(
    page_title="RAG Investment Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.vector_store = None
    st.session_state.embedding_generator = None
    st.session_state.retriever = None
    st.session_state.llm_handler = None
    st.session_state.chunks_loaded = False
    st.session_state.query_history = []


def initialize_system():
    """Initialize all system components"""
    try:
        with st.spinner("Initializing RAG system..."):
            # Validate configuration
            Config.validate()
            
            # Initialize components
            st.session_state.vector_store = VectorStore()
            st.session_state.embedding_generator = EmbeddingGenerator()
            st.session_state.retriever = SemanticRetriever(
                st.session_state.vector_store,
                st.session_state.embedding_generator
            )
            st.session_state.llm_handler = LLMHandler()
            st.session_state.initialized = True
            
            return True
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        return False


def process_pdf(pdf_file, source_name: str):
    """Process uploaded PDF and store in vector database"""
    
    # Save uploaded file temporarily
    temp_path = f"temp_{pdf_file.name}"
    
    try:
        with open(temp_path, "wb") as f:
            f.write(pdf_file.getbuffer())
        
        # Process PDF
        st.info("📄 Extracting text from PDF...")
        processor = PDFProcessor()
        chunks = processor.process_pdf(temp_path, source_name)
        
        # Display chunk statistics
        stats = processor.get_chunk_statistics(chunks)
        st.success(f"✅ Created {stats['total_chunks']} chunks from {stats['pages_covered']} pages")
        
        with st.expander("📊 Chunk Statistics"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Chunks", stats['total_chunks'])
            col2.metric("Pages Covered", stats['pages_covered'])
            col3.metric("Avg Chunk Size", f"{stats['avg_chunk_size']:.0f} chars")
        
        # Generate embeddings
        st.info("🔢 Generating embeddings...")
        progress_bar = st.progress(0)
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = st.session_state.embedding_generator.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
            progress_bar.progress((i + 1) / len(chunks))
        
        st.success("✅ Generated embeddings for all chunks")
        
        # Store in Firebase
        st.info("💾 Storing in Firebase Firestore...")
        stored_count = st.session_state.vector_store.store_chunks_batch(chunks)
        
        st.success(f"✅ Successfully stored {stored_count} chunks in Firebase!")
        st.session_state.chunks_loaded = True
        
        # Display sample chunks
        with st.expander("👀 Sample Chunks (First 2)"):
            for i, chunk in enumerate(chunks[:2]):
                st.markdown(f"**Chunk {i+1}**")
                st.text(chunk['text'][:500] + "...")
                st.json({
                    'chunk_id': chunk['chunk_id'],
                    'metadata': chunk['metadata'],
                    'embedding_preview': chunk['embedding'][:10] + ['...']
                })
                st.divider()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing PDF: {e}")
        return False
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


def display_answer(query: str, result: dict):
    """Display answer with sources"""
    
    # Answer
    st.markdown("### 💡 Answer")
    st.markdown(f"<div class='info-box'>{result['answer']}</div>", unsafe_allow_html=True)
    
    # Sources
    if result.get('sources'):
        with st.expander(f"📚 Sources ({len(result['sources'])} references)"):
            for source in result['sources']:
                st.markdown(f"""
                **Source {source['source_num']}** - Page {source['page']} (Relevance: {source['similarity']:.3f})
                
                {source['text_preview']}
                """)
                st.divider()
    
    # Add to history
    st.session_state.query_history.append({
        'timestamp': datetime.now(),
        'query': query,
        'answer': result['answer']
    })


def main():
    """Main application"""
    
    # Header
    st.markdown("<div class='main-header'>📈 RAG Investment Analysis System</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Stock Market & Investment Analysis using RAG</div>", unsafe_allow_html=True)
    
    # Initialize system
    if not st.session_state.initialized:
        if not initialize_system():
            st.error("System initialization failed. Please check your configuration.")
            st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("📋 System Status")
        
        # Display configuration
        with st.expander("⚙️ Configuration"):
            config_info = Config.display_config()
            for key, value in config_info.items():
                st.text(f"{key}: {value}")
        
        # Collection stats
        if st.button("🔄 Refresh Stats"):
            stats = st.session_state.vector_store.get_collection_stats()
            st.session_state.collection_stats = stats
        
        if hasattr(st.session_state, 'collection_stats'):
            stats = st.session_state.collection_stats
            st.metric("Total Chunks", stats.get('total_chunks', 0))
            if stats.get('sources'):
                st.write("**Sources:**")
                for source in stats['sources']:
                    st.text(f"• {source}")
        
        # Clear database option
        st.divider()
        if st.button("🗑️ Clear Database", type="secondary"):
            if st.checkbox("Are you sure?"):
                deleted = st.session_state.vector_store.delete_all_chunks()
                st.success(f"Deleted {deleted} chunks")
                st.session_state.chunks_loaded = False
                st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload PDF", "🔍 Query System", "📊 View Database", "📝 Assignment Queries"])
    
    # Tab 1: Upload PDF
    with tab1:
        st.header("Upload Investment Book")
        
        st.markdown("""
        <div class='warning-box'>
        <strong>⚠️ Data Privacy Notice:</strong>
        <ul>
            <li>The uploaded book is for educational use only</li>
            <li>Do not share the book or database outside this course</li>
            <li>All data is stored securely in Firebase Firestore</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload your investment textbook in PDF format"
        )
        
        if uploaded_file is not None:
            st.success(f"📄 File uploaded: {uploaded_file.name}")
            
            source_name = st.text_input(
                "Source Name (optional)",
                value=uploaded_file.name.replace('.pdf', ''),
                help="Name to identify this book in the database"
            )
            
            if st.button("🚀 Process and Upload", type="primary"):
                process_pdf(uploaded_file, source_name)
    
    # Tab 2: Query System
    with tab2:
        st.header("Ask Questions")
        
        if not st.session_state.chunks_loaded:
            chunks = st.session_state.vector_store.get_all_chunks(limit=1)
            if chunks:
                st.session_state.chunks_loaded = True
        
        if not st.session_state.chunks_loaded:
            st.warning("⚠️ Please upload a PDF first before querying.")
        else:
            query = st.text_input(
                "Enter your question:",
                placeholder="e.g., How to become an intelligent investor?",
                help="Ask any question about investment and stock markets"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                top_k = st.number_input("Top K Results", min_value=1, max_value=10, value=5)
            with col2:
                temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            
            if st.button("🔍 Search", type="primary") and query:
                with st.spinner("Searching and generating answer..."):
                    # Retrieve relevant chunks
                    retrieved_chunks = st.session_state.retriever.retrieve(query, top_k=top_k)
                    
                    if not retrieved_chunks:
                        st.warning("No relevant information found for your query.")
                    else:
                        # Generate answer
                        result = st.session_state.llm_handler.generate_answer_with_sources(
                            query,
                            retrieved_chunks,
                            temperature=temperature
                        )
                        
                        display_answer(query, result)
    
    # Tab 3: View Database
    with tab3:
        st.header("Database Viewer")
        
        col1, col2 = st.columns(2)
        
        with col1:
            view_limit = st.number_input("Number of chunks to view", min_value=1, max_value=50, value=5)
        
        with col2:
            if st.button("📥 Load Chunks"):
                chunks = st.session_state.vector_store.get_all_chunks(limit=view_limit)
                st.session_state.viewed_chunks = chunks
        
        if hasattr(st.session_state, 'viewed_chunks'):
            chunks = st.session_state.viewed_chunks
            
            if chunks:
                st.success(f"Loaded {len(chunks)} chunks")
                
                for i, chunk in enumerate(chunks):
                    with st.expander(f"Chunk {i+1}: {chunk.get('chunk_id', 'unknown')}"):
                        st.markdown("**Text:**")
                        st.text(chunk.get('text', '')[:1000])
                        
                        st.markdown("**Metadata:**")
                        st.json(chunk.get('metadata', {}))
                        
                        st.markdown("**Embedding (first 10 dimensions):**")
                        embedding = chunk.get('embedding', [])
                        st.code(str(embedding[:10]))
                        st.text(f"Total dimensions: {len(embedding)}")
            else:
                st.info("No chunks found in database")
    
    # Tab 4: Assignment Queries
    with tab4:
        st.header("📝 Mandatory Assignment Queries")
        
        st.markdown("""
        <div class='info-box'>
        These are the required queries for the assignment. Click each button to test your system with the mandatory questions.
        </div>
        """, unsafe_allow_html=True)
        
        mandatory_queries = [
            "how to deal with brokerage houses?",
            "what is theory of diversification?",
            "how to become intelligent investor?",
            "how to do business valuation?",
            "what is putting all eggs in one basket analogy?"
        ]
        
        if not st.session_state.chunks_loaded:
            chunks = st.session_state.vector_store.get_all_chunks(limit=1)
            if chunks:
                st.session_state.chunks_loaded = True
        
        if not st.session_state.chunks_loaded:
            st.warning("⚠️ Please upload a PDF first.")
        else:
            for i, query in enumerate(mandatory_queries, 1):
                st.markdown(f"### Query {i}")
                st.info(f"❓ {query}")
                
                if st.button(f"Run Query {i}", key=f"query_{i}"):
                    with st.spinner(f"Processing query {i}..."):
                        # Retrieve and generate answer
                        retrieved_chunks = st.session_state.retriever.retrieve(query, top_k=5)
                        
                        if retrieved_chunks:
                            result = st.session_state.llm_handler.generate_answer_with_sources(
                                query,
                                retrieved_chunks
                            )
                            display_answer(query, result)
                        else:
                            st.warning("No relevant information found.")
                
                st.divider()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>Assignment:</strong> RAG System Implementation - Stock Market & Investment Analysis</p>
        <p><strong>Instructor:</strong> Achint Setia | <strong>Due Date:</strong> March 5, 2026</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
