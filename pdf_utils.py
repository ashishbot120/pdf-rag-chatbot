import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re 
import os

# (Optional) Set tesseract path manually if not auto-detected
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):
    text = ""

    images = convert_from_path(pdf_path, dpi=300, poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
    for img in images:
        ocr_text = pytesseract.image_to_string(img, config="--psm 6")
        if ocr_text.strip():
            cleaned_text = re.sub(r"\s+", " ", ocr_text).strip()
            text += "\n" + cleaned_text + "\n"

    return text.lower()



    
def chunk_text_with_metadata(text, filename, chunk_size=1000, overlap=200):
    chunks = []
    metadatas = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)

        metadatas.append({
            "filename": filename,
            "chunk_index": chunk_index,
            "start_char": start,
            "end_char": end
        })

        start += chunk_size - overlap
        chunk_index += 1

    return chunks, metadatas

        