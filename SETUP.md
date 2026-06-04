# Setup Guide - RAG Investment Analysis System

## Complete Installation & Configuration Guide

### Step 1: System Requirements

**Required:**
- Python 3.9 or higher
- pip (Python package manager)
- Git
- 4GB+ RAM
- Internet connection

**Accounts Needed:**
- Firebase account (free tier sufficient)
- OpenAI account with API credits (or use free alternatives)

---

### Step 2: Clone and Setup Environment

```bash
# Navigate to your desired directory
cd ~/Documents  # or your preferred location

# Clone repository (if using git)
git clone <your-repo-url>
cd rag-investment-system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

---

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# This will install:
# - Streamlit (web interface)
# - Firebase Admin SDK
# - OpenAI API client
# - PDF processing libraries
# - Sentence Transformers (for embeddings)
# - LangChain (for text processing)
# - And other utilities
```

**If you encounter errors:**
```bash
# Try installing problematic packages individually
pip install streamlit
pip install firebase-admin
pip install openai
pip install PyPDF2 pdfplumber
pip install sentence-transformers
pip install langchain
```

---

### Step 4: Firebase Setup

#### 4.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Enter project name (e.g., "rag-investment-system")
4. Disable Google Analytics (optional for this project)
5. Click "Create Project"

#### 4.2 Enable Firestore Database

1. In Firebase Console, click "Firestore Database" in left sidebar
2. Click "Create Database"
3. Choose "Start in test mode" (for development)
4. Select your preferred region
5. Click "Enable"

#### 4.3 Get Service Account Key

1. In Firebase Console, click gear icon ⚙️ → "Project Settings"
2. Go to "Service Accounts" tab
3. Click "Generate New Private Key"
4. Click "Generate Key" to download JSON file
5. Save the file as `firebase-key.json` in your project root

**Important:** Never commit this file to git!

#### 4.4 Configure Firestore Rules (Optional but Recommended)

In Firestore Console → Rules tab:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;  // For development only
    }
  }
}
```

---

### Step 5: OpenAI API Setup

#### Option A: Using OpenAI (Recommended for best quality)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Click "Create New Secret Key"
5. Copy the key (starts with `sk-`)
6. **Important:** Add credits to your account ($5-10 sufficient for this assignment)

#### Option B: Using Free Alternative (Sentence Transformers)

If you don't want to use OpenAI, the system supports free local embeddings:
- Set `USE_FREE_EMBEDDING=true` in `.env`
- This uses Sentence Transformers locally (no API key needed)
- Note: You'll still need OpenAI for the LLM part, or modify code to use alternatives

---

### Step 6: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Configure `.env` with your credentials:**

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Firebase Configuration
FIREBASE_KEY_PATH=firebase-key.json

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo

# For free embeddings (no OpenAI key needed for embeddings):
# USE_FREE_EMBEDDING=true

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval Configuration
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

---

### Step 7: Verify Installation

```bash
# Test imports
python -c "import streamlit; import firebase_admin; import openai; print('✅ All imports successful!')"

# Check Python version
python --version  # Should be 3.9+

# Verify Firebase key exists
ls firebase-key.json  # Should show the file
```

---

### Step 8: Run the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux

# Run Streamlit app
streamlit run app.py

# The app should open in your browser at http://localhost:8501
```

**First Time Running:**
- The app will initialize Firebase connection
- You'll see the main interface with four tabs
- Check the sidebar for system status

---

### Step 9: Using the System

#### Upload Your Investment Book

1. Go to "📤 Upload PDF" tab
2. Click "Browse files" and select your investment book PDF
3. Optionally edit the source name
4. Click "🚀 Process and Upload"
5. Wait for processing (may take several minutes for large books)

**What happens during upload:**
- PDF text is extracted
- Text is split into ~1000 character chunks
- Each chunk gets a vector embedding
- Everything is stored in Firebase Firestore

#### View Database

1. Go to "📊 View Database" tab
2. Set number of chunks to view
3. Click "📥 Load Chunks"
4. Expand chunks to see:
   - Full text content
   - Metadata (page, source)
   - Vector embeddings

**This is what you'll show in your video recording!**

#### Query the System

1. Go to "🔍 Query System" tab
2. Enter your question
3. Adjust parameters if needed:
   - Top K Results (how many chunks to retrieve)
   - Temperature (creativity of answer)
4. Click "🔍 Search"
5. View answer with sources

#### Run Mandatory Queries

1. Go to "📝 Assignment Queries" tab
2. Click each "Run Query" button
3. Review and scroll through answers slowly for video
4. The 5 mandatory queries are pre-loaded

---

### Step 10: Verify for Assignment Recording

Before recording your video, verify:

**✅ Checklist:**
- [ ] System initializes without errors
- [ ] PDF uploads successfully
- [ ] Firebase console shows chunks in `investment_chunks` collection
- [ ] Can view at least 2 chunks with embeddings in Database tab
- [ ] All 5 mandatory queries produce answers
- [ ] Answers are relevant and based on book content

**View Firebase Console:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Firestore Database
4. You should see `investment_chunks` collection
5. Click on any document to see:
   - `chunk_id`
   - `text` (the chunk content)
   - `embedding` (array of numbers)
   - `metadata` (source, page, etc.)

---

### Step 11: Recording Your Video

**Screen to Show:**

1. **System Initialization** (10 seconds)
   - Show Streamlit app loading
   - Show system status in sidebar

2. **Upload PDF** (1-2 minutes)
   - Navigate to Upload tab
   - Select and upload book
   - Show progress and completion messages
   - Show chunk statistics

3. **Firebase Console** (1-2 minutes)
   - Open Firebase Console in new tab
   - Navigate to Firestore Database
   - Show `investment_chunks` collection
   - Open 2 different documents
   - Zoom in to show:
     - Text content
     - Embedding array (scroll through numbers)
     - Metadata

4. **Database Viewer** (30 seconds)
   - Go to View Database tab in app
   - Load 2-3 chunks
   - Expand and show text + embeddings

5. **Run Mandatory Queries** (3-4 minutes)
   - Go to Assignment Queries tab
   - Run each of the 5 queries one by one
   - Slowly scroll through each answer
   - Show sources for at least one answer

**Recording Tips:**
- Keep your webcam on throughout
- Speak clearly and explain what you're showing
- Scroll slowly through answers so text is readable
- Show both the app and Firebase console
- Total video: 8-12 minutes

---

### Troubleshooting

#### Problem: Firebase Connection Error

```
Solution:
1. Check firebase-key.json exists in project root
2. Verify JSON file is valid (open in text editor)
3. Check Firebase project is created
4. Verify Firestore is enabled
```

#### Problem: OpenAI API Error

```
Solution:
1. Verify API key in .env is correct
2. Check OpenAI account has credits
3. Test API key at https://platform.openai.com/api-keys
4. Alternative: Set USE_FREE_EMBEDDING=true for embeddings
```

#### Problem: PDF Processing Fails

```
Solution:
1. Verify PDF is not password-protected
2. Check PDF has extractable text (not scanned images)
3. Try a different PDF
4. Check Python version (needs 3.9+)
```

#### Problem: No Chunks Found

```
Solution:
1. Check if upload completed successfully
2. Verify Firebase console shows documents
3. Click "🔄 Refresh Stats" in sidebar
4. Try clearing database and re-uploading
```

#### Problem: Poor Answer Quality

```
Solution:
1. Upload more comprehensive investment book
2. Increase Top K Results (try 7-10)
3. Adjust similarity threshold in config
4. Check if query matches book content
```

---

### Alternative Configurations

#### Using Local LLM (Advanced)

To avoid OpenAI costs entirely, you can integrate local models:

```python
# In src/llm_handler.py, add support for:
- Ollama (run Llama locally)
- HuggingFace Transformers
- GPT4All

Example for Ollama:
pip install ollama
# Then modify LLMHandler to use ollama.chat()
```

#### Using Different Vector Database

The system can be adapted to use:
- Pinecone (cloud vector DB)
- Chroma (local vector DB)
- Qdrant (self-hosted)

Replace `VectorStore` class with your preferred solution.

---

### Cost Estimation

**OpenAI Costs (approximate):**
- Embedding 100 pages: ~$0.05
- 10 queries with GPT-3.5-turbo: ~$0.10
- Total for assignment: ~$0.50-$2.00

**Firebase Costs:**
- Free tier includes:
  - 50,000 document reads/day
  - 20,000 document writes/day
  - 1 GB storage
- Should be completely free for this assignment

---

### Project Structure Reference

```
rag-investment-system/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── pdf_processor.py       # PDF extraction & chunking
│   ├── embeddings.py          # Vector embedding generation
│   ├── vector_store.py        # Firebase Firestore operations
│   ├── retriever.py           # Semantic search
│   └── llm_handler.py         # LLM interaction
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── .env.example              # Environment template
├── firebase-key.json         # Firebase credentials (create this)
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
├── SETUP.md                  # This file
└── venv/                     # Virtual environment (created by you)
```

---

### Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Firebase Firestore Guide](https://firebase.google.com/docs/firestore)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [RAG Architecture Guide](https://python.langchain.com/docs/use_cases/question_answering/)

---

### Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check logs in terminal for error messages
4. Ensure all API keys are correctly configured
5. Review Firebase Console for data

**Good luck with your assignment! 🚀**
