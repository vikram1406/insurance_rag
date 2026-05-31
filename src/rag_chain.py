import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vectorstore import get_retriever
from src.utils import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    LLM_MODEL,
    TOP_K_RESULTS,
    check_api_key,
    print_info,
    print_success,
    print_error,
)


def format_context(docs):
    """Convert retrieved documents into context text."""
    context_parts = []

    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("filename", "Unknown file")
        category = doc.metadata.get("category", "Unknown category")
        page = doc.metadata.get("page", "N/A")

        context_parts.append(
            f"""
SOURCE {i}
File: {source}
Category: {category}
Page: {page}

Content:
{doc.page_content}
"""
        )

    return "\n\n".join(context_parts)


def build_prompt(question: str, context: str) -> str:
    """Create final prompt for the LLM."""
    return f"""
You are an insurance assistant.

Answer the user's question using ONLY the context provided below.

Rules:
- Do not make up information.
- If the answer is not present in the context, say: "I could not find this information in the provided policy documents."
- Keep the answer clear and simple.
- Mention relevant policy terms when available.

Context:
{context}

Question:
{question}

Answer:
"""


def call_openrouter(prompt: str) -> str:
    """Call OpenRouter chat completion API."""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.2,
    }

    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    if response.status_code != 200:
        raise Exception(f"OpenRouter API Error: {response.status_code} - {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def answer_question(question: str) -> str:
    """Full RAG pipeline: retrieve context and generate answer."""

    if not check_api_key():
        return "OpenRouter API key missing."

    retriever = get_retriever(k=TOP_K_RESULTS)

    if retriever is None:
        return "Retriever could not be loaded. Please create vectorstore first."

    print_info("Retrieving relevant chunks...")
    docs = retriever.invoke(question)

    if not docs:
        return "No relevant documents found."

    print_success(f"Retrieved {len(docs)} relevant chunks")

    context = format_context(docs)

    prompt = build_prompt(question, context)

    print_info("Generating answer using LLM...")
    answer = call_openrouter(prompt)

    return answer


if __name__ == "__main__":
    question = input("Ask insurance question: ")

    answer = answer_question(question)

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)