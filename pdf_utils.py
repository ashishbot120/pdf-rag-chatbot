from pdf2image import convert_from_bytes
import pytesseract
import re
import os
import platform

# ------------------ FIX PATHS (OS-AWARE) ------------------
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
    POPPLER_PATH = r"C:\poppler\poppler-24.08.0\Library\bin"
else:
    # Linux (Digital Ocean) — installed via apt, no path needed
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    POPPLER_PATH = None  # pdf2image finds it automatically on Linux

# ------------------ OCR EXTRACTION ------------------
def extract_text_from_pdf(pdf_bytes):
    text = ""

    images = convert_from_bytes(
        pdf_bytes,
        dpi=300,
        poppler_path=POPPLER_PATH  # None on Linux = auto-detect
    )

    for img in images:
        ocr_text = pytesseract.image_to_string(img, config="--psm 6")
        if ocr_text.strip():
            cleaned = re.sub(r"\s+", " ", ocr_text)
            text += cleaned + "\n"

    return text.lower()

# ------------------ CHUNKING ------------------
def chunk_text_with_metadata(
    text,
    filename,
    pdf_id,
    chunk_size=1000,
    overlap=200
):
    chunks = []
    metadatas = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        metadatas.append({
            "pdf_id": pdf_id,
            "filename": filename,
            "chunk_index": chunk_index,
            "start_char": start,
            "end_char": end
        })
        start += chunk_size - overlap
        chunk_index += 1

    return chunks, metadatas