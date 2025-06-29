# 📄 PDF RAG Chatbot

A **Streamlit-based AI chatbot** that lets you upload PDFs (text-based or scanned images) and ask questions about their content. It uses OCR (Tesseract), vector embeddings (ChromaDB), and local LLMs (Mistral via Ollama) to provide smart, real-time answers.

---

## 🚀 Features

- ✅ Upload and preview PDFs live in the browser
- ✅ Handles scanned/image-based PDFs using OCR
- ✅ Intelligent chunking with metadata
- ✅ Embedding generation using SentenceTransformers
- ✅ Cosine similarity-based semantic search with ChromaDB
- ✅ Answer generation using local LLM (Mistral via Ollama)
- ✅ Displays the source chunk and location of each answer
- ✅ Streamlit UI for interactive Q&A

---

## 🛠️ Tech Stack

| Layer        | Tool/Library                      |
|--------------|-----------------------------------|
| 🧠 LLM        | Mistral via [Ollama](https://ollama.com/) |
| 📦 Embeddings | SentenceTransformers              |
| 🗃️ Vector DB  | ChromaDB                          |
| 📄 PDF Tools  | PyMuPDF, pytesseract (OCR)        |
| 🌐 Frontend   | Streamlit                         |
| 🧠 Backend    | Python                            |

---

## 📚 My Project Journey

I built this project to understand how Retrieval-Augmented Generation (RAG) works in real-world applications. Here's a breakdown of how I approached it:

### ✅ Step 1: PDF Extraction
- Used **PyMuPDF** to extract text from standard PDFs.
- Added **Tesseract OCR** to handle scanned or image-based PDFs.

### ✅ Step 2: Chunking the Text
- Split long PDFs into chunks with metadata like page number and position.
- Stored both original and summary chunks.

### ✅ Step 3: Embedding and Storage
- Used **SentenceTransformers** to convert chunks into vector embeddings.
- Stored them in **ChromaDB** for fast semantic search.

### ✅ Step 4: Semantic Search
- When a user asks a question, the app:
  - Converts the question into an embedding
  - Finds the most similar chunks using **cosine similarity**
  - Selects the most relevant chunks to answer

### ✅ Step 5: Answer Generation
- Passed the best matching chunks and question into **Mistral LLM via Ollama**.
- Generated responses while showing source chunk info for transparency.

### ✅ Step 6: Streamlit UI
- Designed a clean UI with:
  - File uploader
  - Live PDF preview using `streamlit-pdf-viewer`
  - Chat input and answer display
  - Source chunk highlight

### ✅ Step 7: Optimizations
- Added logic to decide when to use all chunks vs top-k chunks.
- Introduced a summary + chunking method to handle large PDFs.

---

'''
## 📁 Project Structure

pdf-chatbot/
├── backend/
│ ├── streamlit_main.py # Streamlit UI
│ ├── pdf_utils.py # PDF reading and OCR
│ ├── embedder.py # SentenceTransformer embedding
│ ├── semantic_search.py # Cosine similarity search
│ ├── vector_db.py # ChromaDB vector storage
│ ├── llm.py # LLM query handling via Ollama
│ ├── requirements.txt # Python dependencies
│ ├── README.md # Project overview (this file)
│ └── .gitignore # Files to exclude from Git 

'''


---

## 📦 Installation & Setup

# 1. Clone the repository
git clone https://github.com/ashishbot120/pdf-rag-chatbot.git
cd pdf-rag-chatbot

# 2. Set up a virtual environment
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run the app
streamlit run streamlit_main.py
