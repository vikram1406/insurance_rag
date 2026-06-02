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
)


def format_context(docs):
    """Convert retrieved documents into context text."""
    context_parts = []

    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("filename", "Unknown file")
        category = doc.metadata.get("category", "Unknown category")
        page = doc.metadata.get("page", "N/A")
        chunk_id = doc.metadata.get("chunk_id", "N/A")

        context_parts.append(
            f"""
SOURCE {i}
File: {source}
Category: {category}
Page: {page}
Chunk ID: {chunk_id}

Content:
{doc.page_content}
"""
        )

    return "\n\n".join(context_parts)


def format_chat_history(chat_history: list[dict], max_turns: int = 5) -> str:
    """Format recent chat history for prompt."""
    if not chat_history:
        return "No previous conversation."

    recent_history = chat_history[-max_turns:]
    history_text = ""

    for item in recent_history:
        history_text += f"User: {item['question']}\n"
        history_text += f"Assistant: {item['answer']}\n\n"

    return history_text.strip()


def build_retrieval_query(question: str, chat_history: list[dict] | None = None) -> str:
    """
    Build retrieval query.

    If the user asks follow-up questions like:
    - it
    - this
    - isme
    - us policy

    then retriever also gets recent chat history.
    """
    if not chat_history:
        return question

    return f"""
Previous conversation:
{format_chat_history(chat_history, max_turns=2)}

Current question:
{question}
"""


def build_prompt(question: str, context: str, chat_history_text: str) -> str:
    """Create final prompt for the LLM."""
    return f"""
You are an insurance assistant.

Answer the user's question using ONLY the context provided below and the previous conversation.

Rules:
- Do not make up information.
- If the answer is not present in the context, say: "I could not find this information in the provided policy documents."
- Use previous conversation only to understand follow-up words like "it", "this", "isme", "us policy".
- Keep the answer clear and simple.
- If multiple policies have different rules, mention that it depends on the policy.

Previous Conversation:
{chat_history_text}

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
        raise Exception(
            f"OpenRouter API Error: {response.status_code} - {response.text}"
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]


def answer_question(question: str, chat_history: list[dict] | None = None) -> str:
    """Full RAG pipeline: retrieve context and generate answer."""

    if chat_history is None:
        chat_history = []

    if not check_api_key():
        return "OpenRouter API key missing."

    retriever = get_retriever(k=TOP_K_RESULTS)

    if retriever is None:
        return "Retriever could not be loaded. Please create vectorstore first."

    print_info("Retrieving relevant chunks...")

    retrieval_query = build_retrieval_query(question, chat_history)
    docs = retriever.invoke(retrieval_query)

    if not docs:
        return "No relevant documents found."

    print_success(f"Retrieved {len(docs)} relevant chunks")

    context = format_context(docs)
    chat_history_text = format_chat_history(chat_history)

    prompt = build_prompt(question, context, chat_history_text)

    print_info("Generating answer using LLM...")
    answer = call_openrouter(prompt)

    return answer


if __name__ == "__main__":
    chat_history = []

    print("Insurance RAG Assistant with Chat Memory")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("Ask insurance question: ")

        if question.lower().strip() in ["exit", "quit", "q"]:
            print("Goodbye!")
            break

        answer = answer_question(question, chat_history)

        print("\n" + "=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(answer)

        chat_history.append({
            "question": question,
            "answer": answer
        })

        chat_history = chat_history[-5:]