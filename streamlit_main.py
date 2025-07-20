import streamlit as st
import base64
from streamlit_pdf_viewer import pdf_viewer
from pdf_utils import extract_text_from_pdf, chunk_text_with_metadata
from embedder import get_embedding
from llm import generate_answer, map_reduce_summary
from vector_db import (
    store_chunks_in_vector_db,
    query_similar_chunk_from_vector_db,
    get_all_chunks_from_db,
    clear_vector_db  # ✅ Import
)

st.set_page_config(page_title="PDF Chatbot", layout="wide")

st.title("📄 Chat with your PDF")
st.markdown("Upload a PDF, preview its content, and ask questions about it.")

# Session state
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "metadatas" not in st.session_state:
    st.session_state.metadatas = []

# Upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_file.read())

     # ✅ Immediately clear previous data
    cleared_count = clear_vector_db()
    st.success(f"🧹 Cleared {cleared_count} previous chunks from the vector DB.")

    remaining_chunks = get_all_chunks_from_db()
    st.info(f"📦 Vector DB now contains {len(remaining_chunks)} chunks.")



    # PDF Preview
    with st.expander("📄 Live PDF Viewer"):
        pdf_viewer("uploaded.pdf")

    # Progress UI
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Step 1: Extract text
    status_text.text("📖 Extracting text from PDF...")
    text = extract_text_from_pdf("uploaded.pdf")
    progress_bar.progress(30)

    # Step 2: Chunking text
    status_text.text("✂️ Chunking text with metadata...")
    chunks, metadatas = chunk_text_with_metadata(text, filename="uploaded.pdf")
    progress_bar.progress(60)

    # Step 3: Store new chunks
    status_text.text("💾 Storing chunks in vector database...")
    store_chunks_in_vector_db(chunks, metadatas)
    progress_bar.progress(100)

    st.session_state.chunks = chunks
    st.session_state.metadatas = metadatas

    status_text.text("✅ PDF processed successfully.")
    st.success("✅ PDF processed and chunks stored!")

    # Show chunks
    with st.expander("📚 View Extracted Chunks"):
        for i, chunk in enumerate(chunks):
            st.markdown(f"**Chunk {i+1}:**")
            st.code(chunk[:1000])

# 🔍 Auto-detect summary-type questions
def should_use_all_chunks(question: str) -> bool:
    keywords = ["summary", "overview", "timetable", "schedule", "entire", "whole", "explain", "all details"]
    return any(kw in question.lower() for kw in keywords)

# Chat section
if st.session_state.chunks:
    question = st.text_input("🤔 Ask a question about the PDF:")
    use_all_chunks = st.checkbox("🔁 Use all chunks for this question")

    if st.button("Ask") and question.strip():
        with st.spinner("Thinking..."):
            use_all = use_all_chunks or should_use_all_chunks(question)

            if use_all:
                answer = map_reduce_summary(st.session_state.chunks)

                st.markdown("### 📋 Summary Answer")
                st.write(answer)

                st.markdown("#### 🔍 Source Info")
                st.write(f"📘 Used **all {len(st.session_state.chunks)} chunks** from the document.")
            else:
                best_chunk_list, metadata_list = query_similar_chunk_from_vector_db(question, top_k=1)

                if best_chunk_list:
                    best_chunk = best_chunk_list[0]
                    metadata = metadata_list[0]

                    context = f"Answer the question using the context below:\n\nContext: {best_chunk}\n\nQuestion: {question}"
                    answer = generate_answer(context)

                    st.markdown("### ✅ Answer")
                    st.write(answer)

                    st.markdown("#### 🔍 Source Info")
                    st.write(f"📄 **Filename:** `{metadata['filename']}`")
                    st.write(f"🔢 **Character Range:** `{metadata['start_char']} - {metadata['end_char']}`")
                    st.code(best_chunk[:300])
                else:
                    st.warning("❌ No relevant content found. Try enabling 'Use all chunks'.")
