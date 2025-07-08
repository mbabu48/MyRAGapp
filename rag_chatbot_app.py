import streamlit as st
from core_rag import CoreRAG
from config import load_config
import re

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

st.title("RAG Chatbot Demo 🤖")
st.write("Ask questions about your ingested Markdown files!")

# Load config and initialize CoreRAG
config = load_config()
core_rag = CoreRAG(config)

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Define assistant's role and capabilities
ASSISTANT_ROLE = (
    "I am a very knowledgeable bot on the [aws-samples](https://github.com/aws-samples) GitHub organization's markdown pages. "
    "I can provide you with detailed information, summaries, and answers about any project, documentation, or topic found in those markdown files. "
    "Ask me anything about AWS Samples repositories, features, usage, or best practices!"
)

ASSISTANT_WITH_DISCLAIMER_ROLE = (
    "I am a very knowledgeable bot on the [aws-samples](https://github.com/aws-samples) GitHub organization's markdown pages. "
    "I can provide you with detailed information, summaries, and answers about any project, documentation, or topic found in those markdown files. "
    "Ask me anything about AWS Samples repositories, features, usage, or best practices!"
    "\n\n**Disclaimer:** I do not have access to the internet or real-time data. My responses are based on the information available in the ingested markdown files. "
    " Please do fact check and verify any critical information from the original sources."
)

# Display chat history
if not st.session_state.messages:
    # On first load, show assistant's introduction
    st.session_state.messages.append({"role": "assistant", "content": ASSISTANT_WITH_DISCLAIMER_ROLE})
    #st.chat_message("assistant").write(ASSISTANT_ROLE)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])
    #print(" \n -------- \n")

# User input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # Handle basic questions about assistant's capabilities
    basic_questions = [
        "what can you do for me",
        "how can you help me",
        "who are you",
        "what is your role",
        "what do you know"
    ]
    if any(q in user_input.lower() for q in basic_questions):
        answer_display = ASSISTANT_ROLE
    else:
        # Query the RAG backend
        with st.spinner("Thinking..."):
            try:
                response = core_rag.query(user_input)
                print(f"Response from core_rag: {response}")
                answer = response.get("answer", "No answer found.")
                print(f"Answer: {answer}")
                sources = response.get("sources", [])
                references = []
                for idx, metadata in enumerate(sources, 1):
                    meta = metadata.get("metadata", {})
                    org_name = meta.get("org_name", "unknown_org")
                    repo_name = meta.get("repository_name", "unknown_repo")
                    file_path = meta.get("markdown_file", "unknown_file")
                    header1 = meta.get("Header 1", "")
                    header2 = meta.get("Header 2", "")
                    header3 = meta.get("Header 3", "")
                    # Remove all non-ASCII characters from headings
                    def clean_heading(h):
                        return re.sub(r'[^\x00-\x7F]+', '', str(h)).lower().lstrip().rstrip().replace(' ', '-').replace('/', '-').replace(':', '').replace('?', '').replace('!', '').replace('.', '').replace(',', '')
                    header1_clean = clean_heading(header1)
                    header2_clean = clean_heading(header2)
                    header3_clean = clean_heading(header3)
                    url = f"http://github.com/{org_name.lstrip('/')}/{repo_name.lstrip('/')}/blob/master/{file_path.lstrip('/')}"
                    if header3_clean:
                        url = f"{url}#-{header3_clean}-"
                    elif header2_clean:
                        url = f"{url}#-{header2_clean}"
                    elif header1_clean:
                        url = f"{url}#{header1_clean}"
                    references.append(f"{idx}. [{url}]({url})")
                if answer.__contains__("The provided context does not contain any information"):
                # If the answer contains the RAG context message, provide a generic reference
                    answer_display = f"{answer}\n\n**References:**\n1. [https://docs.aws.amazon.com/](https://docs.aws.amazon.com/)"
                else:
                    if references:
                        refs_md = "\n".join(references)
                        answer_display = f"{answer}\n\n**References:**\n{refs_md}"
                    else:
                        answer_display = answer
            except Exception as e:
                answer_display = f"Error: {e}"
                print(f"Error during query: {e}")

    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": answer_display})

    # Display assistant response
    st.chat_message("assistant").write(answer_display)