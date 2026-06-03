import os
import sys
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

from src.utils import (
    VECTORSTORE_DIR,
    EMBEDDING_MODEL,
    print_success,
    print_warning,
    print_info,
)

from src.ingestion import run_ingestion_pipeline


class SentenceTransformerEmbeddings(Embeddings):

    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode(text).tolist()


def get_embedding_function():

    print_info(f"Loading embedding model: {EMBEDDING_MODEL}")

    return SentenceTransformerEmbeddings(
        EMBEDDING_MODEL
    )


def create_vectorstore(reset=False):

    if reset and os.path.exists(VECTORSTORE_DIR):

        print_warning("Deleting old vectorstore...")

        shutil.rmtree(VECTORSTORE_DIR)

    chunks = run_ingestion_pipeline()

    if not chunks:
        print_warning("No chunks found.")
        return None

    embedding_function = get_embedding_function()

    print_info("Creating Chroma vectorstore...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=VECTORSTORE_DIR,
        collection_name="insurance_rag"
    )

    print_success("Vectorstore created successfully!")

    return vectorstore


def load_vectorstore():

    if not os.path.exists(VECTORSTORE_DIR):

        print_warning("Vectorstore not found.")

        return None

    embedding_function = get_embedding_function()

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embedding_function,
        collection_name="insurance_rag"
    )

    print_success("Vectorstore loaded successfully!")

    return vectorstore


def get_retriever(k=5):
    vectorstore = load_vectorstore()

    if vectorstore is None:
        return None

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": 20,
            "lambda_mult": 0.5
        }
    )


if __name__ == "__main__":

    create_vectorstore(reset=True)