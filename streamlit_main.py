import streamlit as st
import base64
from dotenv import load_dotenv

# 🔑 Load environment variables (OpenRouter key)
load_dotenv()

from streamlit_pdf_viewer import pdf_viewer
from pdf_utils import extract_text_from_pdf, chunk_text_with_metadata
from embedder import get_embedding
from llm import generate_answer, map_reduce_summary
from vector_db import (
    store_chunks_in_vector_db,
    query_similar_chunk_from_vector_db,
    get_all_chunks_from_db,
    clear_vector_db
)

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="PDF Chatbot", layout="wide")

st.title("📄 Chat with your PDF")
st.markdown("Upload a PDF, preview its content, and ask questions about it.")

# ------------------ SESSION STATE ------------------
if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "metadatas" not in st.session_state:
    st.session_state.metadatas = []

# ------------------ FILE UPLOAD ------------------
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    with open("uploaded.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # 🧹 Clear previous vectors
    cleared_count = clear_vector_db()
    st.success(f"🧹 Cleared {cleared_count} previous chunks from the vector DB.")

    remaining_chunks = get_all_chunks_from_db()
    st.info(f"📦 Vector DB now contains {len(remaining_chunks)} chunks.")

    # ------------------ PDF PREVIEW ------------------
    with st.expander("📄 Live PDF Viewer"):
        pdf_viewer("uploaded.pdf")

    # ------------------ PROGRESS UI ------------------
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Step 1: Extract text
    status_text.text("📖 Extracting text from PDF...")
    text = extract_text_from_pdf("uploaded.pdf")
    progress_bar.progress(30)

    # Step 2: Chunking
    status_text.text("✂️ Chunking text with metadata...")
    chunks, metadatas = chunk_text_with_metadata(text, filename="uploaded.pdf")
    progress_bar.progress(60)

    # Step 3: Store vectors
    status_text.text("💾 Storing chunks in vector database...")
    store_chunks_in_vector_db(chunks, metadatas)
    progress_bar.progress(100)

    st.session_state.chunks = chunks
    st.session_state.metadatas = metadatas

    status_text.text("✅ PDF processed successfully.")
    st.success("✅ PDF processed and chunks stored!")

    # ------------------ SHOW CHUNKS ------------------
    with st.expander("📚 View Extracted Chunks"):
        for i, chunk in enumerate(chunks):
            st.markdown(f"**Chunk {i + 1}:**")
            st.code(chunk[:1000])

# ------------------ SUMMARY DETECTION ------------------
def should_use_all_chunks(question: str) -> bool:
    keywords = [
        "summary", "overview", "entire", "whole",
        "explain", "all details", "timetable", "schedule"
    ]
    return any(kw in question.lower() for kw in keywords)

# ------------------ CHAT SECTION ------------------
if st.session_state.chunks:
    question = st.text_input("🤔 Ask a question about the PDF:")
    use_all_chunks = st.checkbox("🔁 Use all chunks for this question")

    if st.button("Ask") and question.strip():
        with st.spinner("🤖 Thinking..."):
            use_all = use_all_chunks or should_use_all_chunks(question)

            # 🔁 FULL DOCUMENT MODE
            if use_all:
                answer = map_reduce_summary(st.session_state.chunks)

                st.markdown("### 📋 Summary Answer")
                st.write(answer)

                st.markdown("#### 🔍 Source Info")
                st.write(f"📘 Used **all {len(st.session_state.chunks)} chunks** from the document.")

            # 🎯 RETRIEVAL MODE
            else:
                best_chunk_list, metadata_list = query_similar_chunk_from_vector_db(
                    question,
                    top_k=1
                )

                if best_chunk_list:
                    best_chunk = best_chunk_list[0]
                    metadata = metadata_list[0]

                    context = (
                        "Answer the question using ONLY the context below.\n\n"
                        f"Context:\n{best_chunk}\n\n"
                        f"Question:\n{question}"
                    )

                    answer = generate_answer(context)

                    st.markdown("### ✅ Answer")
                    st.write(answer)

                    st.markdown("#### 🔍 Source Info")
                    st.write(f"📄 **Filename:** `{metadata['filename']}`")
                    st.write(
                        f"🔢 **Character Range:** "
                        f"`{metadata['start_char']} - {metadata['end_char']}`"
                    )
                    st.code(best_chunk[:300])

                else:
                    st.warning("❌ No relevant content found. Try enabling 'Use all chunks'.")
