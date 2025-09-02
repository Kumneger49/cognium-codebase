import os
import json
import asyncio
import logging
from typing import Optional, Any, List, Dict

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
    # print(file_path)
    return file_path


def _read_doc_status() -> Dict[str, Any]:
    try:
        with open(os.path.join("rag_storage", "kv_store_doc_status.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def list_processed_docs() -> List[Dict[str, Any]]:
    """List processed documents from rag_storage and output folder."""
    status = _read_doc_status()
    items: List[Dict[str, Any]] = []
    for doc_id, meta in status.items():
        items.append(
            {
                "doc_id": doc_id,
                "file_path": meta.get("file_path", "unknown"),
                "updated_at": meta.get("updated_at", ""),
                "chunks_count": meta.get("chunks_count", 0),
            }
        )

    # Also scan output directory to show available parsed folders
    output_docs = []
    if os.path.isdir("output"):
        for name in os.listdir("output"):
            sub = os.path.join("output", name)
            if os.path.isdir(sub):
                output_docs.append(name)

    # Enrich listing with output presence
    for item in items:
        item["output_exists"] = item.get("file_path", "") and any(
            item["file_path"].split(".")[0] in d or d in item["file_path"] for d in output_docs
        )
    return sorted(items, key=lambda x: x.get("updated_at", ""), reverse=True)


class StreamlitLogHandler(logging.Handler):
    def __init__(self, placeholder: "st.delta_generator.DeltaGenerator"):
        super().__init__(level=logging.INFO)
        self.placeholder = placeholder
        self._lines: List[str] = []

    def emit(self, record):
        try:
            msg = self.format(record)
            # Make messages more readable
            msg = msg.replace("INFO:", "").replace("WARNING:", "⚠️  ")
            self._lines.append(msg)
            # Keep last 120 lines
            if len(self._lines) > 120:
                self._lines = self._lines[-120:]
            # Render as small markdown log
            safe = "\n".join(f"- {line}" for line in self._lines)
            self.placeholder.markdown(safe)
        except Exception:
            pass


def main() -> None:
    st.set_page_config(page_title="RAGAnything Demo", page_icon="📄", layout="wide")
    st.title("RAGAnything Demo")
    st.caption("Upload a PDF and ask questions with hybrid retrieval.")
 

    with st.sidebar:
        st.subheader("Documents")
        docs = list_processed_docs()
        if docs:
            labels = [f"{d['file_path']}  •  {d['chunks_count']} chunks" for d in docs]
            idx = st.selectbox("Processed", options=list(range(len(docs))), format_func=lambda i: labels[i]) if docs else None
            if idx is not None:
                st.caption(f"Doc ID: {docs[idx]['doc_id']}  |  Updated: {docs[idx]['updated_at']}")
        else:
            st.caption("No processed documents yet")

        st.divider()
        uploaded_file = st.file_uploader("Upload a PDF or TXT", type=["pdf", "txt"], accept_multiple_files=False)
        ingest_hint = st.caption("Upload to add another file to the knowledge base.")
    file_path_for_the_apploaded_file = None

    if uploaded_file is not None:
        file_path_for_the_apploaded_file = save_uploaded_file(uploaded_file)
    print(f"the new file path created: {file_path_for_the_apploaded_file}")

 
    st.markdown("### Ask a question")
    user_query = st.text_input(
        "Ask a question",
        placeholder="e.g., Summarize the document",
        label_visibility="collapsed",
    )
    ask_clicked = st.button("Ask", use_container_width=True)
    if ask_clicked:
        if not user_query.strip():
            st.error("Enter a question to ask.")
            st.stop()  # stops further execution
        if file_path_for_the_apploaded_file is None and not docs:
            st.error("Please upload a file or select an already processed one.")
            st.stop()

        # only runs if inputs are valid
        trace_expander = st.expander("Pipeline activity", expanded=True)
        log_placeholder = trace_expander.empty()
        handler = StreamlitLogHandler(log_placeholder)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        lg = logging.getLogger("lightrag")
        lg.addHandler(handler)
        lg.setLevel(logging.INFO)

        try:
            with st.status("Retrieving and generating answer...", expanded=True) as status:
                status.update(label="Parsing/Loading, building context...", state="running")
                question = f"""
                            You are acting as a research assistant for an investment company. 
                            You will receive a document (financial report, news article, company profile, or market analysis). 

                            Your task: Carefully analyze the document and directly answer the user query. 
                            - Use only the content relevant to the query. 
                            - If the query asks broadly, highlight information investors care about (e.g., financial performance, growth potential, risks, competitive positioning, management quality, market opportunities). 
                            - If the query is specific, focus only on that aspect. Do not introduce unrelated metrics. 
                            - If the document lacks enough detail, acknowledge the gaps clearly. 

                            User Query: {user_query}
                        """

                # Prefer selected processed doc if no new upload
                file_arg = file_path_for_the_apploaded_file
                if file_arg is None and docs:
                    # Use a sentinel filename to indicate existing KB; backend should skip insertion via dedupe
                    # We pass the selected doc's file name (friendly for logs) but it will hit parse cache
                    file_arg = os.path.join("data", docs[idx]["file_path"]) if idx is not None else None

                answer = asyncio.run(
                    backend_main(query=question, file_path=file_arg)
                )
                status.update(label="Answer ready", state="complete")
                st.markdown("### Answer")
                st.write(answer)
        except Exception as exc:
            st.error(f"Query failed: {exc}")
        finally:
            lg.removeHandler(handler)




if __name__ == "__main__":
    main()


