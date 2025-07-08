import streamlit as st
from core_rag import CoreRAG
from config import load_config

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

st.title("RAG Chatbot Demo 🤖")
st.write("Ask questions about your ingested Markdown files!")

# Load config and initialize CoreRAG
config = load_config()
core_rag = CoreRAG(config)

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input
user_input = st.chat_input("Type your question here...")

# Add user message to history and display immediately
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Query the RAG backend
    with st.spinner("Thinking..."):
        try:
            # The response should be a dict with 'answer' and 'source' keys
            response = core_rag.query(user_input)
            # Example: response = {"answer": "...", "source": "aws-samples/repo/path/to/file.md"}
            answer = response.get("answer", "No answer found.")
            source = response.get("source", None)
            if source:
                # Build the GitHub URL
                github_url = f"http://github.com/aws-samples/{source.lstrip('/')}"
                answer_display = f"{answer}\n\n**Source:** [{source}]({github_url})"
            else:
                answer_display = answer
        except Exception as e:
            answer_display = f"Error: {e}"

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": answer_display})
    st.chat_message("assistant").write(answer_display)

# Display chat history (excluding the latest user/assistant messages just shown above)
for msg in st.session_state.messages[:-2 if user_input else None]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])