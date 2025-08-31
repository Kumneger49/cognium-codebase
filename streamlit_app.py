import os
import asyncio
from typing import Optional, Any

import streamlit as st

from main import main as backend_main

import asyncio


def save_uploaded_file(uploaded_file):
    """Saves the uploaded file to a specified directory."""
    # Create the directory if it doesn't exist
    upload_dir = "data"
    os.makedirs(upload_dir, exist_ok=True)

    # Construct the full path for the new file
    file_path = os.path.join(upload_dir, uploaded_file.name)

    # Write the file's content to the new file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    print(file_path)
    return file_path


def main() -> None:
    st.set_page_config(page_title="RAGAnything Demo", page_icon="📄", layout="wide")
    st.title("RAGAnything Demo")
    st.caption("Upload a PDF and ask questions with hybrid retrieval.")
 

    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf", "txt"], accept_multiple_files=False)
    file_path_for_the_apploaded_file = None

    if uploaded_file is not None:
        file_path_for_the_apploaded_file = save_uploaded_file(uploaded_file)
    print(f"the new file path created: {file_path_for_the_apploaded_file}")

 
    question = st.text_input("Ask a question", placeholder="e.g., Summarize the document")
    question = f"""You are a helpful assistant. The user provides a document and asks a question: {question}. 
    Retrieve the most relevant information from the document and present it in a clear, structured format (e.g., bullet points, numbered steps, or sections). 
    Ensure the answer is concise, accurate, and easy to understand."""
    ask_clicked = st.button("Ask", use_container_width=True)

    if ask_clicked:
        if not question.strip():
            st.warning("Enter a question to ask.")
        elif file_path_for_the_apploaded_file is None:
            st.error("Please upload a file before asking a question.")
        else:
            with st.spinner("Retrieving and generating answer..."):
                try:
                    answer = asyncio.run(backend_main(query=question, file_path= file_path_for_the_apploaded_file))
                    st.write(answer)
                except Exception as exc:
                    st.error(f"Query failed: {exc}")



if __name__ == "__main__":
    main()


