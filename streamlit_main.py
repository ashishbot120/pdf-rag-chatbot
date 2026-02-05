import streamlit as st
from dotenv import load_dotenv
import base64

# ------------------ LOAD ENV ------------------
load_dotenv()

# ------------------ IMPORTS ------------------

from pdf_utils import extract_text_from_pdf, chunk_text_with_metadata
from llm import generate_answer, map_reduce_summary
from vector_db import (
    store_chunks_in_vector_db,
    query_similar_chunk_from_vector_db,
    clear_vector_db
)
from storage import upload_pdf

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="PDF Chatbot",
    layout="wide"
)

st.title("📄 Chat with your PDF")
st.markdown("Upload a PDF, preview it, and ask questions based on its content.")

# ------------------ SESSION STATE ------------------
if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "metadatas" not in st.session_state:
    st.session_state.metadatas = []

if "pdf_id" not in st.session_state:
    st.session_state.pdf_id = None

# ------------------ FILE UPLOAD ------------------
uploaded_file = st.file_uploader(
    "📤 Upload a PDF file",
    type="pdf"
)

if uploaded_file:
    pdf_bytes = uploaded_file.getvalue()

    # 🔼 Upload PDF to Supabase
    with st.spinner("☁️ Uploading PDF to cloud storage..."):
        pdf_meta = upload_pdf(pdf_bytes, uploaded_file.name)
        st.session_state.pdf_id = pdf_meta["pdf_id"]

    st.success("✅ PDF uploaded successfully")

    # 🧹 Clear previous vectors (single-PDF mode)
    clear_vector_db()
    st.info("🧹 Vector database reset for new PDF")

    # ------------------ PDF VIEWER ------------------
    with st.expander("📄 Preview PDF"):
        def show_pdf(pdf_bytes):
            base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
            pdf_display = f"""
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" 
                height="600px"
                type="application/pdf">
            </iframe>
            """
            st.write(pdf_display, unsafe_allow_html=True)  # show_pdf(pdf_bytes)

    # ------------------ PROCESSING UI ------------------
    progress = st.progress(0)
    status = st.empty()

    # 1️⃣ Extract text
    status.text("📖 Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_bytes)
    progress.progress(30)

    # 2️⃣ Chunk text
    status.text("✂️ Chunking text with metadata...")
    chunks, metadatas = chunk_text_with_metadata(
        text,
        filename=uploaded_file.name,
        pdf_id=st.session_state.pdf_id
    )
    progress.progress(60)

    # 3️⃣ Store vectors
    status.text("💾 Storing chunks in vector database...")
    store_chunks_in_vector_db(chunks, metadatas)
    progress.progress(100)

    st.session_state.chunks = chunks
    st.session_state.metadatas = metadatas

    status.text("✅ PDF processed successfully")
    st.success("🎉 PDF processed and indexed!")

    # ------------------ SHOW CHUNKS ------------------
    with st.expander("📚 View Extracted Chunks"):
        for i, chunk in enumerate(chunks):
            st.markdown(f"**Chunk {i + 1}**")
            st.code(chunk[:1000])

# ------------------ SUMMARY INTENT DETECTION ------------------
def should_use_all_chunks(question: str) -> bool:
    keywords = [
        "summary", "overview", "entire", "whole",
        "explain", "all details", "timetable", "schedule"
    ]
    return any(k in question.lower() for k in keywords)

# ------------------ CHAT SECTION ------------------
if st.session_state.chunks:
    st.divider()
    st.subheader("💬 Ask Questions")

    question = st.text_input("🤔 Ask something about the PDF")
    use_all_chunks = st.checkbox("🔁 Use full document (summary mode)")

    if st.button("Ask") and question.strip():
        with st.spinner("🤖 Thinking..."):
            use_all = use_all_chunks or should_use_all_chunks(question)

            # 📘 FULL DOCUMENT MODE
            if use_all:
                answer = map_reduce_summary(st.session_state.chunks)

                st.markdown("### 📋 Answer (Full Document)")
                st.write(answer)

                st.caption(
                    f"Used all {len(st.session_state.chunks)} chunks"
                )

            # 🎯 RETRIEVAL MODE
            else:
                best_chunks, metadatas = query_similar_chunk_from_vector_db(
                question=question,
                pdf_id=st.session_state.pdf_id,
                top_k=1
                )

                if best_chunks:
                    chunk = best_chunks[0]
                    metadata = metadatas[0]

                    prompt = (
                        "Answer the question using ONLY the context below.\n\n"
                        f"Context:\n{chunk}\n\n"
                        f"Question:\n{question}"
                    )

                    answer = generate_answer(prompt)

                    st.markdown("### ✅ Answer")
                    st.write(answer)

                    st.markdown("#### 🔍 Source")
                    st.write(f"📄 File: `{metadata['filename']}`")
                    st.write(
                        f"🔢 Characters: "
                        f"{metadata['start_char']} – {metadata['end_char']}"
                    )
                    st.code(chunk[:400])

                else:
                    st.warning("❌ No relevant chunk found. Try full document mode.")
