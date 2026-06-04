"""
Quick setup test to verify all dependencies are installed
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import firebase_admin
        print("✅ Firebase Admin imported successfully")
    except ImportError as e:
        print(f"❌ Firebase Admin import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ pdfplumber import failed: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✅ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        return False
    
    try:
        import langchain
        print("✅ langchain imported successfully")
    except ImportError as e:
        print(f"❌ langchain import failed: {e}")
        return False
    
    return True

def test_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")
    
    try:
        sys.path.insert(0, 'src')
        from config import Config
        print("✅ config module imported successfully")
    except ImportError as e:
        print(f"❌ config module import failed: {e}")
        return False
    
    try:
        from pdf_processor import PDFProcessor
        print("✅ pdf_processor module imported successfully")
    except ImportError as e:
        print(f"❌ pdf_processor module import failed: {e}")
        return False
    
    try:
        from embeddings import EmbeddingGenerator
        print("✅ embeddings module imported successfully")
    except ImportError as e:
        print(f"❌ embeddings module import failed: {e}")
        return False
    
    try:
        from vector_store import VectorStore
        print("✅ vector_store module imported successfully")
    except ImportError as e:
        print(f"❌ vector_store module import failed: {e}")
        return False
    
    try:
        from retriever import SemanticRetriever
        print("✅ retriever module imported successfully")
    except ImportError as e:
        print(f"❌ retriever module import failed: {e}")
        return False
    
    try:
        from llm_handler import LLMHandler
        print("✅ llm_handler module imported successfully")
    except ImportError as e:
        print(f"❌ llm_handler module import failed: {e}")
        return False
    
    return True

def check_config_files():
    """Check if required config files exist"""
    import os
    print("\nChecking configuration files...")
    
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("❌ .env file not found")
        return False
    
    if os.path.exists('firebase-key.json'):
        print("✅ firebase-key.json file exists")
    else:
        print("⚠️  firebase-key.json NOT found (you need to download this from Firebase)")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print(" RAG Investment System - Setup Test")
    print("="*60)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test modules
    if not test_modules():
        success = False
    
    # Check config files
    if not check_config_files():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✅ SETUP TEST PASSED!")
        print("\n📋 Next Steps:")
        print("1. Get your Firebase key from Firebase Console")
        print("2. Save it as 'firebase-key.json' in project root")
        print("3. Add your OpenAI API key to .env file")
        print("4. Run: streamlit run app.py")
    else:
        print("❌ SETUP TEST FAILED")
        print("Please fix the errors above")
    print("="*60)
