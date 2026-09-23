from pathlib import Path
import hashlib

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
from pypdf import PdfReader


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "Mydocuments"

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)


# ============================================================
# TEXT SPLITTER
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(

    chunk_size=1000,

    chunk_overlap=200

)


# ============================================================
# EMBEDDING MODEL
# ============================================================

embeddings = HuggingFaceEmbeddings(

    model_name="sentence-transformers/all-MiniLM-L6-v2"

)


# ============================================================
# CHROMA VECTOR DATABASE
# ============================================================

vector_store = Chroma(

    collection_name="document_collection",

    embedding_function=embeddings,

    persist_directory="./chroma_db"

)


# ============================================================
# GEMINI
# ============================================================

llm = ChatGoogleGenerativeAI(

    model="gemini-2.5-flash"

)


# ============================================================
# CONVERSATION HISTORY
# ============================================================

messages = []


# ============================================================
# CHECK FILE TYPE
# ============================================================

def allowed_file(filename):

    extension = Path(filename).suffix.lower()

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# CREATE UNIQUE ID FOR EACH CHUNK
# ============================================================

def create_chunk_id(

    file_path,
    page,
    chunk_number,
    content

):

    unique_text = (

        f"{file_path}|"
        f"{page}|"
        f"{chunk_number}|"
        f"{content}"

    )

    return hashlib.sha256(

        unique_text.encode("utf-8")

    ).hexdigest()


# ============================================================
# READ A FILE
# ============================================================

def read_file(file_path):

    file_path = Path(file_path)

    documents = []


    # ========================================================
    # PDF
    # ========================================================

    if file_path.suffix.lower() == ".pdf":

        reader = PdfReader(file_path)


        for page_number, page in enumerate(

            reader.pages,

            start=1

        ):

            text = page.extract_text() or ""


            if text.strip():

                documents.append({

                    "path": str(file_path),

                    "filename": file_path.name,

                    "page": page_number,

                    "content": text

                })


    # ========================================================
    # TXT / MARKDOWN
    # ========================================================

    else:

        content = file_path.read_text(

            encoding="utf-8",

            errors="ignore"

        )


        if content.strip():

            documents.append({

                "path": str(file_path),

                "filename": file_path.name,

                "page": None,

                "content": content

            })


    return documents


# ============================================================
# DELETE OLD CHUNKS OF A FILE
# ============================================================

def delete_existing_file_chunks(file_path):

    file_path = str(Path(file_path))


    try:

        existing = vector_store.get(

            where={

                "path": file_path

            }

        )


        ids = existing.get("ids", [])


        if ids:

            vector_store.delete(

                ids=ids

            )

            print(

                f"Deleted {len(ids)} old chunks from "
                f"{Path(file_path).name}"

            )


    except Exception as error:

        print(

            "Could not delete old chunks:",

            error

        )


# ============================================================
# INDEX DOCUMENT
# ============================================================

def index_document(file_path):

    print(

        f"\nIndexing: {Path(file_path).name}"

    )


    # --------------------------------------------------------
    # Remove old version first
    # --------------------------------------------------------

    delete_existing_file_chunks(

        file_path

    )


    # --------------------------------------------------------
    # Read document
    # --------------------------------------------------------

    documents = read_file(

        file_path

    )


    if not documents:

        return 0


    texts = []

    metadatas = []

    ids = []


    # ========================================================
    # CREATE CHUNKS
    # ========================================================

    for document in documents:

        document_chunks = text_splitter.split_text(

            document["content"]

        )


        for chunk_number, chunk in enumerate(

            document_chunks

        ):

            metadata = {

                "source":
                document["filename"],

                "path":
                document["path"],

                "page":
                document["page"]
                if document["page"] is not None
                else 0,

                "chunk":
                chunk_number

            }


            chunk_id = create_chunk_id(

                document["path"],

                document["page"],

                chunk_number,

                chunk

            )


            texts.append(chunk)

            metadatas.append(metadata)

            ids.append(chunk_id)


    # ========================================================
    # ADD TO CHROMA
    # ========================================================

    if texts:

        vector_store.add_texts(

            texts=texts,

            metadatas=metadatas,

            ids=ids

        )


    print(

        f"Added {len(texts)} chunks."

    )


    return len(texts)


# ============================================================
# INDEX ALL EXISTING FILES
# ============================================================

def index_existing_documents():

    print("\nChecking existing documents...")


    indexed_files = set()


    for file_path in Path(

        UPLOAD_FOLDER

    ).rglob("*"):

        if not file_path.is_file():

            continue


        if not allowed_file(

            file_path.name

        ):

            continue


        file_key = str(file_path)


        if file_key in indexed_files:

            continue


        indexed_files.add(file_key)


        # ----------------------------------------------------
        # IMPORTANT
        # Remove old chunks and create fresh chunks
        # ----------------------------------------------------

        index_document(

            file_path

        )


    print(

        "\nDocument indexing completed."

    )


# ============================================================
# STARTUP INDEXING
# ============================================================

index_existing_documents()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    document_names = sorted(

        list(

            set(

                file_path.name

                for file_path in Path(

                    UPLOAD_FOLDER

                ).rglob("*")

                if file_path.is_file()

                and allowed_file(

                    file_path.name

                )

            )

        )

    )


    return render_template(

        "index.html",

        documents=document_names,

        document_count=len(document_names)

    )


# ============================================================
# UPLOAD FILE
# ============================================================

@app.route(

    "/upload",

    methods=["POST"]

)
def upload_file():

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if "file" not in request.files:

        return jsonify({

            "error":
            "No file selected."

        }), 400


    file = request.files["file"]


    # --------------------------------------------------------
    # Check filename
    # --------------------------------------------------------

    if file.filename == "":

        return jsonify({

            "error":
            "Please select a file."

        }), 400


    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if not allowed_file(

        file.filename

    ):

        return jsonify({

            "error":
            "Only PDF, TXT and Markdown files are allowed."

        }), 400


    # --------------------------------------------------------
    # Secure filename
    # --------------------------------------------------------

    filename = secure_filename(

        file.filename

    )


    file_path = Path(

        app.config["UPLOAD_FOLDER"]

    ) / filename


    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    file.save(file_path)


    # --------------------------------------------------------
    # Index document
    # --------------------------------------------------------

    try:

        chunk_count = index_document(

            file_path

        )

    except Exception as error:

        print(

            "Indexing error:",

            error

        )

        return jsonify({

            "error":
            "The file could not be processed."

        }), 500


    # --------------------------------------------------------
    # Check whether text was extracted
    # --------------------------------------------------------

    if chunk_count == 0:

        return jsonify({

            "error":
            "No readable text was found in the file."

        }), 400


    return jsonify({

        "message":
        f"{filename} uploaded successfully.",

        "filename":
        filename,

        "chunks":
        chunk_count

    })


# ============================================================
# ASK QUESTION
# ============================================================

@app.route(

    "/ask",

    methods=["POST"]

)
def ask():

    global messages


    # --------------------------------------------------------
    # Get user question
    # --------------------------------------------------------

    data = request.get_json()

    if not data:

        return jsonify({

            "error":
            "Invalid request."

        }), 400


    user_input = data.get(

        "message",

        ""

    ).strip()


    if not user_input:

        return jsonify({

            "error":
            "Please enter a question."

        }), 400


    # ========================================================
    # CREATE FRESH RETRIEVER
    # ========================================================

    # This makes sure the latest uploaded documents
    # are available for retrieval.

    retriever = vector_store.as_retriever(

        search_kwargs={

            "k": 4

        }

    )


    # ========================================================
    # RETRIEVE DOCUMENTS
    # ========================================================

    try:

        retrieved_documents = retriever.invoke(

            user_input

        )

    except Exception as error:

        print(

            "Retrieval error:",

            error

        )

        return jsonify({

            "error":
            "Could not search the document database."

        }), 500


    # ========================================================
    # CHECK RETRIEVAL
    # ========================================================

    if not retrieved_documents:

        return jsonify({

            "answer":
            "I could not find this information "
            "in the provided documents.",

            "sources": []

        })


    # ========================================================
    # CREATE CONTEXT
    # ========================================================

    context_parts = []

    sources = []


    for document in retrieved_documents:

        source = document.metadata.get(

            "source",

            "Unknown"

        )


        page = document.metadata.get(

            "page",

            0

        )


        if page and page != 0:

            source_text = (

                f"{source} - Page {page}"

            )

        else:

            source_text = source


        context_parts.append(

            f"""
SOURCE:
{source_text}

CONTENT:
{document.page_content}
"""

        )


        source_info = {

            "source":
            source,

            "page":
            page if page != 0 else None

        }


        if source_info not in sources:

            sources.append(

                source_info

            )


    context = "\n\n".join(

        context_parts

    )


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = f"""

You are an AI document assistant.

Your job is to answer the user's question
using ONLY the retrieved document context.

IMPORTANT RULES:

1. Use only the information in the context.
2. Do not invent information.
3. If the answer is not present in the context,
   say exactly:

"I could not find this information
in the provided documents."

4. Give a clear and useful answer.
5. If the context contains information from
   multiple documents, combine the relevant
   information carefully.
6. Do not mention information that is not
   supported by the retrieved context.

RETRIEVED DOCUMENT CONTEXT:

{context}

"""


    # ========================================================
    # CREATE CONVERSATION
    # ========================================================

    conversation = [

        SystemMessage(

            content=system_prompt

        )

    ]


    # Previous conversation
    conversation.extend(

        messages[-6:]

    )


    # Current question
    conversation.append(

        HumanMessage(

            content=user_input

        )

    )


    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        response = llm.invoke(

            conversation

        )

    except Exception as error:

        print(

            "Gemini error:",

            error

        )

        return jsonify({

            "error":
            "Gemini could not generate a response."

        }), 500


    # ========================================================
    # SAVE CHAT HISTORY
    # ========================================================

    messages.append(

        HumanMessage(

            content=user_input

        )

    )


    messages.append(

        response

    )


    # Keep history small
    messages = messages[-10:]


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return jsonify({

        "answer":
        response.content,

        "sources":
        sources

    })


# ============================================================
# CLEAR CHAT
# ============================================================

@app.route(

    "/clear",

    methods=["POST"]

)
def clear_chat():

    global messages

    messages = []


    return jsonify({

        "message":
        "Chat cleared"

    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True

    )