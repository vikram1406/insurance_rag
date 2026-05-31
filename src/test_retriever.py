import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vectorstore import get_retriever
from src.utils import print_info, print_success, print_error


def test_retriever():
    retriever = get_retriever(k=5)

    if retriever is None:
        print_error("Retriever could not be loaded.")
        return

    question = "What are the exclusions in health insurance policy?"

    print_info(f"Question: {question}")

    results = retriever.invoke(question)

    print_success(f"Retrieved {len(results)} chunks")

    for i, doc in enumerate(results, start=1):
        print_info("=" * 80)
        print_info(f"Result {i}")
        print(doc.page_content[:1000])
        print("\nMetadata:")
        print(doc.metadata)


if __name__ == "__main__":
    test_retriever()