# RAG System - Stock Market & Investment Analysis

## Project Overview
A Retrieval-Augmented Generation (RAG) system built for analyzing investment textbooks and answering queries about stock market and investment strategies.

## Features
- PDF ingestion and intelligent text chunking
- Vector embeddings using OpenAI/Sentence-Transformers
- Firebase Firestore for vector storage
- Semantic search and retrieval
- LLM-powered answer generation
- Interactive web interface

## Architecture
```
PDF Upload → Text Extraction → Chunking → Embedding Generation → 
Vector Store (Firebase) → Query → Semantic Search → LLM → Answer
```

## Tech Stack
- **Backend**: Python 3.9+
- **Vector Database**: Firebase Firestore
- **Embeddings**: OpenAI API / Sentence-Transformers
- **LLM**: OpenAI GPT-4 / GPT-3.5-turbo
- **PDF Processing**: PyPDF2, pdfplumber
- **UI**: Streamlit
- **Vector Search**: FAISS / Custom similarity search

## Project Structure
```
rag-investment-system/
├── src/
│   ├── pdf_processor.py      # PDF extraction and chunking
│   ├── embeddings.py          # Generate vector embeddings
│   ├── vector_store.py        # Firebase operations
│   ├── retriever.py           # Semantic search
│   ├── llm_handler.py         # LLM integration
│   └── config.py              # Configuration
├── app.py                     # Streamlit application
├── requirements.txt           # Dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
└── README.md                 # Documentation
```

## Installation

### Prerequisites
- Python 3.9 or higher
- Firebase account with Firestore enabled
- OpenAI API key (or use free alternatives)

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd rag-investment-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Setup Firebase**
- Create a Firebase project
- Enable Firestore Database
- Download service account key JSON
- Place it in the project root as `firebase-key.json`

## Usage

### Run the Application
```bash
streamlit run app.py
```

### Upload Investment Book
1. Open the web interface (default: http://localhost:8501)
2. Upload your investment textbook PDF
3. Wait for processing and embedding generation
4. View chunks and embeddings in Firebase console

### Query the System
Enter questions like:
- "how to deal with brokerage houses?"
- "what is theory of diversification?"
- "how to become intelligent investor?"
- "how to do business valuation?"
- "what is putting all eggs in one basket analogy?"

## Mandatory Test Queries
1. how to deal with brokerage houses?
2. what is theory of diversification?
3. how to become intelligent investor?
4. how to do business valuation?
5. what is putting all eggs in one basket analogy?

## Configuration

### Chunking Strategy
- Chunk size: 1000 tokens (adjustable)
- Overlap: 200 tokens
- Method: Recursive character splitting with semantic boundaries

### Embedding Model
- Default: OpenAI `text-embedding-3-small`
- Alternative: `sentence-transformers/all-MiniLM-L6-v2` (free)

### LLM Model
- Default: OpenAI `gpt-3.5-turbo`
- Alternative: `gpt-4` for better quality

## Firebase Schema

### Collection: `investment_chunks`
```json
{
  "chunk_id": "unique_id",
  "text": "chunk content",
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "source": "book_name.pdf",
    "page": 42,
    "chunk_index": 15
  },
  "created_at": "timestamp"
}
```

## Development

### Code Structure
- `pdf_processor.py`: Handles PDF extraction and intelligent chunking
- `embeddings.py`: Manages embedding generation (OpenAI/HuggingFace)
- `vector_store.py`: Firebase CRUD operations
- `retriever.py`: Implements semantic search and ranking
- `llm_handler.py`: LLM query and response generation
- `app.py`: Streamlit UI and orchestration

## Data Privacy & Ethics
⚠️ **Important Notes:**
- Source material is for educational use only
- Do not share the book or database outside this course
- Ensure chunks accurately represent source text
- Avoid hallucination in generated responses

## Assignment Compliance
This system fulfills all requirements:
- ✅ PDF ingestion and processing
- ✅ Vector embedding generation
- ✅ Firebase storage with viewable chunks and embeddings
- ✅ Semantic retrieval
- ✅ Response generation for mandatory queries
- ✅ Video recording ready interface

## Troubleshooting

### Common Issues
1. **Firebase connection error**: Verify `firebase-key.json` path
2. **OpenAI API error**: Check API key in `.env`
3. **Memory error during PDF processing**: Reduce chunk size
4. **Slow embedding generation**: Consider using batch processing

## License
Educational use only - Assignment for Stock Market & Investment Analysis course

## Author
Name: [Your Name]
Roll Number: [Your Roll Number]
Instructor: Achint Setia
Date: March 5, 2026
