"""
PDF Processing Module
Handles PDF text extraction and intelligent chunking
"""

import re
from typing import List, Dict
import PyPDF2
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import Config


class PDFProcessor:
    """Process PDF files and split into chunks"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
        
        # Initialize text splitter with semantic separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
    
    def extract_text_pypdf2(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF using PyPDF2
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with page text and metadata
        """
        pages_data = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    text = page.extract_text()
                    
                    if text.strip():
                        pages_data.append({
                            'page_number': page_num,
                            'text': text,
                            'method': 'PyPDF2'
                        })
        except Exception as e:
            print(f"Error extracting with PyPDF2: {e}")
            
        return pages_data
    
    def extract_text_pdfplumber(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF using pdfplumber (better for complex layouts)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with page text and metadata
        """
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    if text and text.strip():
                        pages_data.append({
                            'page_number': page_num,
                            'text': text,
                            'method': 'pdfplumber'
                        })
        except Exception as e:
            print(f"Error extracting with pdfplumber: {e}")
            
        return pages_data
    
    def extract_text(self, pdf_path: str, method: str = 'auto') -> List[Dict]:
        """
        Extract text from PDF using specified or automatic method
        
        Args:
            pdf_path: Path to PDF file
            method: 'pypdf2', 'pdfplumber', or 'auto'
            
        Returns:
            List of dictionaries with page text and metadata
        """
        if method == 'pypdf2':
            return self.extract_text_pypdf2(pdf_path)
        elif method == 'pdfplumber':
            return self.extract_text_pdfplumber(pdf_path)
        else:  # auto
            # Try pdfplumber first (better quality), fallback to PyPDF2
            pages = self.extract_text_pdfplumber(pdf_path)
            if not pages:
                pages = self.extract_text_pypdf2(pdf_path)
            return pages
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (simple heuristic)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
        
        return text.strip()
    
    def create_chunks(self, pages_data: List[Dict], source_name: str) -> List[Dict]:
        """
        Create chunks from extracted pages
        
        Args:
            pages_data: List of page data dictionaries
            source_name: Name of the source PDF
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        chunk_index = 0
        
        for page_data in pages_data:
            page_num = page_data['page_number']
            text = self.clean_text(page_data['text'])
            
            if not text:
                continue
            
            # Split page text into chunks
            page_chunks = self.text_splitter.split_text(text)
            
            for chunk_text in page_chunks:
                chunks.append({
                    'chunk_id': f"{source_name}_chunk_{chunk_index}",
                    'text': chunk_text,
                    'metadata': {
                        'source': source_name,
                        'page': page_num,
                        'chunk_index': chunk_index,
                        'chunk_size': len(chunk_text)
                    }
                })
                chunk_index += 1
        
        return chunks
    
    def process_pdf(self, pdf_path: str, source_name: str = None) -> List[Dict]:
        """
        Complete PDF processing pipeline
        
        Args:
            pdf_path: Path to PDF file
            source_name: Optional name for the source (defaults to filename)
            
        Returns:
            List of processed chunks with metadata
        """
        if source_name is None:
            source_name = pdf_path.split('/')[-1].replace('.pdf', '')
        
        print(f"Extracting text from {pdf_path}...")
        pages_data = self.extract_text(pdf_path)
        
        if not pages_data:
            raise ValueError("No text could be extracted from PDF")
        
        print(f"Extracted {len(pages_data)} pages")
        
        print("Creating chunks...")
        chunks = self.create_chunks(pages_data, source_name)
        
        print(f"Created {len(chunks)} chunks")
        
        return chunks
    
    def get_chunk_statistics(self, chunks: List[Dict]) -> Dict:
        """
        Get statistics about the chunks
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {}
        
        chunk_sizes = [len(chunk['text']) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'total_characters': sum(chunk_sizes),
            'pages_covered': len(set(chunk['metadata']['page'] for chunk in chunks))
        }


# Test function
if __name__ == "__main__":
    processor = PDFProcessor()
    print("PDF Processor initialized")
    print(f"Chunk size: {processor.chunk_size}")
    print(f"Chunk overlap: {processor.chunk_overlap}")
