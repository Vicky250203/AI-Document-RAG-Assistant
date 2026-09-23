# RAG_File_Retrival
 This prroject is about # 🤖 AI Document RAG Assistant

An AI-powered multi-document question-answering application built using **Python, Flask, Google Gemini, HuggingFace Embeddings, ChromaDB, and LangChain**.

The application allows users to upload PDF, TXT, and Markdown documents and ask questions about their content. Instead of sending the entire document directly to the LLM, the application uses Retrieval-Augmented Generation (RAG) to retrieve the most relevant document chunks and provide them to Gemini for generating a grounded response.

# Features

-Upload PDF, TXT, and Markdown documents
-Semantic document search
-Automatic document chunking
-HuggingFace sentence embeddings
-ChromaDB vector database
-Google Gemini 2.5 Flash
-LangChain-based RAG pipeline
-Interactive chat interface
-Source/page information for retrieved content
-Re-index uploaded documents
-Prevents duplicate document chunks
-Clear conversation history
-Flask web application
-Responsive web interface


# Architecture

The application follows a Retrieval-Augmented Generation architecture.


                    USER
                      │
                      ▼
             ┌─────────────────┐
             │  Flask Web App  │
             └────────┬────────┘
                      │
                 Upload File
                      │
                      ▼
             ┌─────────────────┐
             │ Document Loader │
             │ PDF/TXT/MD      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Text Splitter   │
             │ Chunking        │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ HuggingFace     │
             │ Embeddings      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │    ChromaDB     │
             │ Vector Database │
             └────────┬────────┘
                      │
                User Question
                      │
                      ▼
             ┌─────────────────┐
             │ Semantic Search │
             │ Top K Chunks    │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Gemini 2.5 Flash│
             │      LLM        │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Answer + Sources│
             └─────────────────┘
The rag that retrives the files from the directory and answer to the user queries
RAG stands for Retrieval-Augmented Generation.

Instead of asking the LLM to answer a question only from its pretrained knowledge, this application first searches the uploaded documents for relevant information.

The process is:

User Question
      ↓
Convert Question into Embedding
      ↓
Search ChromaDB
      ↓
Retrieve Relevant Chunks
      ↓
Send Chunks + Question to Gemini
      ↓
Generate Answer

This helps the application answer questions based on the user's uploaded documents.

Document Processing Pipeline

When a user uploads a document:

Document
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding Generation
   ↓
Vector Storage
   ↓
ChromaDB

For example, a large document can be divided into smaller chunks:

Document
│
├── Chunk 1
├── Chunk 2
├── Chunk 3
├── Chunk 4
└── ...

Each chunk is converted into a numerical vector using the HuggingFace embedding model.

Question Answering Pipeline

When the user asks a question:

Question
   ↓
Retriever
   ↓
ChromaDB
   ↓
Top 4 Relevant Chunks
   ↓
Context
   ↓
Gemini 2.5 Flash
   ↓
Answer
   ↓
Sources

The application uses the retrieved context to generate a grounded response.

# Technologies Used
# Technology	Purpose
1. Python	Core programming language
2. Flask	Web application backend
3. LangChain	LLM/RAG framework
4. Google Gemini	Large Language Model
5. HuggingFace	Text embeddings
6. Sentence Transformers	Embedding model
7. ChromaDB	Vector database
8. PyPDF	PDF text extraction
9. HTML	Frontend structure
10. CSS	Frontend styling
11. JavaScript	Frontend interaction
# Embedding Model

The project uses:

sentence-transformers/all-MiniLM-L6-v2

This model converts text into vector representations that can be used for semantic similarity search.

# LLM

The application uses:

Gemini 2.5 Flash

Gemini receives the retrieved document context and generates the final answer.

# Project Structure

AI-Document-RAG-Assistant/
│
├── app.py
│
├── requirements.txt
│
├── .env
│
├── README.md
│
├── Mydocuments/
│   └── uploaded documents
│
├── chroma_db/
│   └── vector database
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js


# Installation
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Document-RAG-Assistant.git

Move into the project directory:

cd AI-Document-RAG-Assistant
2. Create a virtual environment

Windows:

python -m venv .venv

Activate it:

.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
 API Key Configuration

Create a .env file in the project root:

GOOGLE_API_KEY=your_google_api_key_here

Do not upload your API key to GitHub.

Add .env to .gitignore.

▶ Run the Application

Start the Flask application:

python app.py

You should see something similar to:

# Running on http://127.0.0.1:5000 

Open the URL in your browser:

http://127.0.0.1:5000

# Uploading Documents

The application supports:

PDF
TXT
Markdown

Select a document from the browser and click:

Upload

The application will:

Save the document.
Extract the text.
Split the text into chunks.
Generate embeddings.
Store the vectors in ChromaDB.
Make the document available for semantic search.
 Asking Questions

After uploading a document, enter a question in the chat interface.

Example:

What are the main skills mentioned in the document?

The application retrieves relevant chunks and sends them to Gemini.

The response also displays the document source and page number when available.

 Duplicate Indexing Prevention

The application removes previously indexed chunks for a document before indexing its updated version.

Existing Document
       ↓
Delete Old Chunks
       ↓
Read Updated Document
       ↓
Create New Chunks
       ↓
Generate Embeddings
       ↓
Store in ChromaDB

This prevents repeated uploads of the same document from continuously creating duplicate vector entries.

 Security Notes

Never commit your API key.

Your .gitignore should contain:

.env
.venv/
__pycache__/
*.pyc
chroma_db/

You should also avoid uploading private documents.

 requirements.txt

The main dependencies are:

flask
python-dotenv
pypdf
langchain
langchain-core
langchain-google-genai
langchain-huggingface
langchain-chroma
langchain-text-splitters
sentence-transformers

Install them using:

pip install -r requirements.txt
 Use Cases

This project can be used for:

Personal document search
Resume analysis
Research document analysis
Company documentation search
Technical documentation Q&A
Study material assistant
PDF question answering
Knowledge base assistants
🔮 Future Improvements

Possible future improvements include:

1. User authentication
2. Multiple document collections
3. Delete documents from the UI
4. Document management dashboard
5. Advanced metadata filtering
6. RAG evaluation
7. Retrieval performance monitoring
8. OCR support for scanned PDFs
9. Voice-based document questions
10. Persistent conversation history
11. Docker deployment
12. Cloud deployment
13. Streaming Gemini responses
14. Author

Vignesha Moorthy V

MCA Graduate | Python | GenAI | RAG | LangChain | AI/ML | Flask

 Project Goal

This project was developed to understand and implement a practical Retrieval-Augmented Generation (RAG) system using modern Generative AI technologies.

The project demonstrates the complete pipeline from:

Document Ingestion
       ↓
Text Processing
       ↓
Chunking
       ↓
Embeddings
       ↓
Vector Database
       ↓
Semantic Retrieval
       ↓
LLM Generation
       ↓
Source-Grounded Answer

---

# 3. Create `.gitignore`

This is **very important** before pushing to GitHub.

Create a file named:

```text
.gitignore

Put this inside:

.env
.venv/
venv/
__pycache__/
*.pyc
chroma_db/
.idea/
.vscode/
Why?

Your .env contains your Gemini API key.

You must not upload it to GitHub.

Also, you don't need to upload:

.venv/
chroma_db/

The virtual environment is recreated with pip install, and the Chroma database is generated locally.

4. Create requirements.txt

In your PyCharm terminal:

pip freeze > requirements.txt

However, for a clean GitHub project, I recommend keeping the requirements focused. You can use:

flask
python-dotenv
pypdf
langchain
langchain-core
langchain-google-genai
langchain-huggingface
langchain-chroma
langchain-text-splitters
sentence-transformers
5. Your final project should look like this
File_retrival/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── Mydocuments/

I recommend not pushing your actual Mydocuments files if they contain personal/private documents.