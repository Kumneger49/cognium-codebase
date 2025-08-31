## RAGAnything Demo (Python + Streamlit)

Simple RAG pipeline that ingests PDFs, builds a local store/knowledge graph, and answers questions via OpenAI models. A Streamlit app is included for uploading documents and querying.

---

## Prerequisites
- Python 3.11.9 or newer
- An OpenAI API key

---

## Quickstart (local)

1) Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
python -V   # should print 3.11.9 or above
```

2) Install dependencies
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

3) Configure your OpenAI API key
```bash
export OPENAI_API_KEY="your_api_key_here"
```
Optionally, create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

4) Run the Streamlit app
```bash
python -m streamlit run streamlit_app.py
```
Then open the provided local URL in your browser. In the sidebar you can:
- Paste/OpenAI key (auto-filled from `OPENAI_API_KEY` if set)
- Choose working/output directories
- Choose parse/retrieval modes
- Upload a PDF, click Ingest, then ask a question

5) (Optional) Run the example script (non-UI)
```bash
python main.py
```

---

## Project structure
- `main.py` — async example: ingest a sample PDF and run a hybrid query
- `streamlit_app.py` — Streamlit UI: upload → ingest → query
- `requirements.txt` — dependencies
- `rag_storage/` — local working store (chunks, entities, relationships, caches)
- `output/` — per-document outputs (markdown, images, intermediates)

---

## Configuration notes
- Models:
  - Text LLM: `gpt-4o-mini`
  - VLM: `gpt-4o` (for multimodal/image cases)
  - Embeddings: `text-embedding-3-large`
- Parser: `mineru` by default; parse methods include `auto`, `ocr`, or `txt`
- Working/output dirs can be changed in the Streamlit sidebar

---

## Troubleshooting

- If Streamlit or packages install into the wrong environment, run commands with your venv explicitly:
```bash
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m streamlit run streamlit_app.py
```

- If you see a numpy/pandas binary mismatch (e.g., "numpy.dtype size changed"):
```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade --force-reinstall numpy pandas
```

- If ingestion fails on a PDF, try a different parse method in the UI (e.g., `ocr` or `auto`) and ensure `./data`, `./rag_storage`, and `./output` are writable.

---

## Roadmap / Next Steps

### 1) Incremental ingestion: keep updating the KG without disruption
- Reuse the same `working_dir` across ingestions. Call `process_document_complete` for each new file; artifacts accumulate in `rag_storage`.
- Deduplicate chunks by stable content hash or document-id + page-range to avoid duplication on re-ingest.
- Keep per-document outputs under `./output/<doc-name>/...` for provenance.
- Example ingestion loop (pseudo-code):
```python
files = ["./data/file1.pdf", "./data/file2.pdf", "./data/file3.pdf"]
for path in files:
    await rag.process_document_complete(
        file_path=path,
        output_dir="./output",
        parse_method="auto",  # or txt/ocr
    )
```
- Consider an "append mode" that records document metadata (doc_id, source, timestamp) so the retriever can filter/scope queries by document or time.

### 2) Conversation memory
- Short-term memory (UI level): keep `st.session_state["chat_history"]` as a list of messages and prepend/include it when calling the LLM. Keep the vector-retrieval step focused on the user’s latest question but provide memory to the generator.
- Long-term memory (RAG level): index summarized conversation turns into the same vector store under a dedicated collection/namespace (e.g., `conversations/`), and retrieve them alongside document chunks.
- Hybrid approach: summarize older turns into compact notes stored as retrievable context; keep last N raw turns for recency.

### 3) Resilience and edge cases
- Retries with backoff for API calls; circuit-breaker on repeated failures.
- Explicit checks: API key presence, file type/size, writable paths.
- Parse fallbacks: try `txt → auto → ocr` in order; surface detailed errors in the UI.
- Idempotency: safe to re-run ingestion for the same file (guard by doc hash/digest).
- Observability: structured logs; capture exceptions with user-friendly messages; optionally write an error report to `./output/errors/<timestamp>.log`.

### 4) Demo agent with web search and weather
- Add two tools:
  - Web search (e.g., Google Custom Search or SerpAPI) → returns top results (title, snippet, url)
  - Weather (e.g., Open-Meteo or OpenWeather) → current conditions by city/lat-lon
- Agent loop options:
  - Simple rules: if the user asks about "weather" or "search", call the tool and blend results with RAG context.
  - LLM tool-calling: expose JSON function specs for `web_search(query)` and `weather(city_or_coords)` and let the LLM decide.
- Streamlit integration: a second tab with an agent chat UI showing tool calls and results alongside RAG citations.

---

## License
This repository is for demonstration purposes. Add your preferred license if needed.


