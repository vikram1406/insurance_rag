import os
import sys
import re
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    LIFE_DIR, GENERAL_DIR, DATABASE_DIR,
    CHUNK_SIZE, CHUNK_OVERLAP,
    print_success, print_warning, print_error, print_info
)

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def clean_text(text: str) -> str:
    """Apply lightweight generic cleaning based on R&D findings."""
    text = text.replace("\uf0b7", "•")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)
    return text.strip()


def generate_chunk_hash(text: str, source: str = "") -> str:
    """
    Generate a stable unique hash for each chunk.

    Why:
    - Helps track chunks uniquely
    - Helps detect duplicate chunks
    - Helps future document/version updates
    """
    hash_input = f"{source}::{text}".encode("utf-8")
    return hashlib.md5(hash_input).hexdigest()


def load_single_file(file_path: str) -> list[Document]:
    """Load one file and return a list of LangChain Document objects."""
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            loader = PyMuPDFLoader(file_path)
            docs = loader.load()

        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()

        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
            docs = loader.load()

        elif ext == ".csv":
            loader = CSVLoader(file_path, encoding="utf-8")
            docs = loader.load()

        else:
            print_warning(f"Skipping unsupported file: {file_path}")
            return []

        category = _get_category(file_path)

        for doc in docs:
            doc.page_content = clean_text(doc.page_content)
            doc.metadata["source"] = file_path
            doc.metadata["category"] = category
            doc.metadata["filename"] = os.path.basename(file_path)

        print_success(f"Loaded: {os.path.basename(file_path)} ({len(docs)} pages/sections)")
        return docs

    except Exception as e:
        print_error(f"Failed to load {os.path.basename(file_path)}: {e}")
        return []


def _get_category(file_path: str) -> str:
    path_lower = file_path.lower()

    if "life" in path_lower:
        return "Life Insurance"
    elif "health" in path_lower:
        return "Health Insurance"
    elif "motor" in path_lower:
        return "Motor Insurance"
    elif "travel" in path_lower:
        return "Travel Insurance"
    elif "home" in path_lower:
        return "Home Insurance"
    elif "general" in path_lower:
        return "General Insurance"
    elif "database" in path_lower:
        return "Insurance Database"

    return "General"


def load_directory(directory: str) -> list[Document]:
    """Walk a directory and load every supported file."""
    all_docs = []
    supported = {".pdf", ".txt", ".md", ".csv"}

    if not os.path.exists(directory):
        print_warning(f"Directory not found: {directory}")
        return []

    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in supported:
                full_path = os.path.join(root, file)
                docs = load_single_file(full_path)
                all_docs.extend(docs)

    return all_docs


def load_all_documents() -> list[Document]:
    """Load every document from life/, general/, and database/ folders."""
    print_info("Starting document ingestion pipeline...")
    print_info("=" * 50)

    all_docs = []

    print_info("Loading Life Insurance documents...")
    life_docs = load_directory(LIFE_DIR)
    all_docs.extend(life_docs)
    print_success(f"Life Insurance: {len(life_docs)} document sections loaded\n")

    print_info("Loading General Insurance documents...")
    general_docs = load_directory(GENERAL_DIR)
    all_docs.extend(general_docs)
    print_success(f"General Insurance: {len(general_docs)} document sections loaded\n")

    print_info("Loading Insurance Database documents...")
    db_docs = load_directory(DATABASE_DIR)
    all_docs.extend(db_docs)
    print_success(f"Insurance Database: {len(db_docs)} rows/sections loaded\n")

    print_info("=" * 50)
    print_success(f"TOTAL documents loaded: {len(all_docs)}")
    return all_docs


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into smaller overlapping chunks.

    R&D decision:
    - Recursive chunking preserves paragraph/sentence boundaries better.
    - chunk_size=1000 and chunk_overlap=200 gave a good balance.
    - Very small chunks are removed.
    - Hash mapping is added for chunk tracking and duplicate detection.
    """
    print_info(f"Splitting documents into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    chunks = [
        chunk for chunk in chunks
        if len(chunk.page_content.strip()) >= 100
    ]

    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get("source", "")

        chunk.metadata["chunk_id"] = generate_chunk_hash(
            chunk.page_content,
            source
        )

        chunk.metadata["chunk_index"] = i

    print_success(f"Created {len(chunks)} chunks from {len(documents)} document sections")
    return chunks


def run_ingestion_pipeline() -> list[Document]:
    """Run the complete ingestion pipeline and return chunks."""
    documents = load_all_documents()

    if not documents:
        print_error("No documents loaded! Check your data/ folder.")
        return []

    chunks = split_documents(documents)

    print_info("\n📊 INGESTION SUMMARY")
    print_info("=" * 50)

    categories = {}
    for chunk in chunks:
        cat = chunk.metadata.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in categories.items():
        print_info(f"  {cat}: {count} chunks")

    print_info("=" * 50)
    print_success("Ingestion pipeline completed successfully!")
    return chunks


if __name__ == "__main__":
    chunks = run_ingestion_pipeline()

    print_info("\nSample chunk content:")
    print_info("-" * 40)

    if chunks:
        print(chunks[0].page_content[:500])
        print_info("-" * 40)
        print_info(f"Metadata: {chunks[0].metadata}")