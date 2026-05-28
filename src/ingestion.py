import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    LIFE_DIR, GENERAL_DIR, DATABASE_DIR,
    CHUNK_SIZE, CHUNK_OVERLAP,
    print_success, print_warning, print_error, print_info
)

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    CSVLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# ── 1. Load a single file based on its extension ───────────────────────────
def load_single_file(file_path: str) -> list[Document]:
    """Load one file and return a list of LangChain Document objects."""
    ext = os.path.splitext(file_path)[1].lower()
    docs = []

    try:
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            docs   = loader.load()

        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
            docs   = loader.load()

        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
            docs   = loader.load()

        elif ext == ".csv":
            loader = CSVLoader(file_path, encoding="utf-8")
            docs   = loader.load()

        else:
            print_warning(f"Skipping unsupported file: {file_path}")
            return []

        # Tag every document with its source folder category
        category = _get_category(file_path)
        for doc in docs:
            doc.metadata["source"]   = file_path
            doc.metadata["category"] = category
            doc.metadata["filename"] = os.path.basename(file_path)

        print_success(f"Loaded: {os.path.basename(file_path)} ({len(docs)} pages/sections)")
        return docs

    except Exception as e:
        print_error(f"Failed to load {os.path.basename(file_path)}: {e}")
        return []


# ── 2. Decide the category label from the file path ───────────────────────
def _get_category(file_path: str) -> str:
    path_lower = file_path.lower()
    if "life"     in path_lower:
        return "Life Insurance"
    elif "general" in path_lower:
        return "General Insurance"
    elif "database" in path_lower:
        return "Insurance Database"
    return "General"


# ── 3. Load all files from a directory (recursive) ────────────────────────
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
                docs      = load_single_file(full_path)
                all_docs.extend(docs)

    return all_docs


# ── 4. Load ALL insurance documents ───────────────────────────────────────
def load_all_documents() -> list[Document]:
    """Load every document from life/, general/, and database/ folders."""
    print_info("Starting document ingestion pipeline...")
    print_info("=" * 50)

    all_docs = []

    # Life Insurance documents
    print_info("Loading Life Insurance documents...")
    life_docs = load_directory(LIFE_DIR)
    all_docs.extend(life_docs)
    print_success(f"Life Insurance: {len(life_docs)} document sections loaded\n")

    # General Insurance documents
    print_info("Loading General Insurance documents...")
    general_docs = load_directory(GENERAL_DIR)
    all_docs.extend(general_docs)
    print_success(f"General Insurance: {len(general_docs)} document sections loaded\n")

    # Database / CSV documents
    print_info("Loading Insurance Database (CSV)...")
    db_docs = load_directory(DATABASE_DIR)
    all_docs.extend(db_docs)
    print_success(f"Insurance Database: {len(db_docs)} rows loaded\n")

    print_info("=" * 50)
    print_success(f"TOTAL documents loaded: {len(all_docs)}")
    return all_docs


# ── 5. Split documents into chunks ────────────────────────────────────────
def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split large documents into smaller overlapping chunks.

    Why RecursiveCharacterTextSplitter?
    - Tries to split on paragraphs first, then sentences, then words
    - Preserves meaning better than fixed-size splitting
    - Overlap ensures context is not lost at chunk boundaries
    """
    print_info(f"Splitting documents into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size        = CHUNK_SIZE,
        chunk_overlap     = CHUNK_OVERLAP,
        length_function   = len,
        separators        = ["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    print_success(f"Created {len(chunks)} chunks from {len(documents)} document sections")
    return chunks


# ── 6. Full pipeline: load + split ────────────────────────────────────────
def run_ingestion_pipeline() -> list[Document]:
    """Run the complete ingestion pipeline and return chunks."""
    # Step 1: Load all documents
    documents = load_all_documents()

    if not documents:
        print_error("No documents loaded! Check your data/ folder.")
        return []

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    # Step 3: Print summary
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


# ── 7. Run directly to test ────────────────────────────────────────────────
if __name__ == "__main__":
    chunks = run_ingestion_pipeline()
    print_info(f"\nSample chunk content:")
    print_info("-" * 40)
    if chunks:
        print(chunks[0].page_content[:500])
        print_info("-" * 40)
        print_info(f"Metadata: {chunks[0].metadata}")