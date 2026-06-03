import streamlit as st
from src.rag_chain import answer_question

st.set_page_config(
    page_title="Insurance AI Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Insurance AI Assistant")
st.write("Ask questions about insurance policies.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input(
    "Enter your question:",
    placeholder="What are the exclusions in this policy?"
)

if st.button("Ask"):

    if question.strip():

        with st.spinner("Thinking..."):

            answer = answer_question(
                question,
                st.session_state.chat_history
            )

            st.session_state.chat_history.append({
                "question": question,
                "answer": answer
            })

            st.session_state.chat_history = (
                st.session_state.chat_history[-5:]
            )

        st.success("Answer Generated")

        st.write("### Answer")
        st.write(answer)

st.divider()

st.subheader("Conversation History")

for chat in reversed(st.session_state.chat_history):

    st.markdown(
        f"""
**User:** {chat['question']}

**Assistant:** {chat['answer']}
"""
    )