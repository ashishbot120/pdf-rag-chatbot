import os
import uuid
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

BUCKET_NAME = "pdfs"

def upload_pdf(file_bytes: bytes, filename: str) -> dict:
    """
    Upload PDF to Supabase Storage and store metadata in DB
    """
    try:
        pdf_id = str(uuid.uuid4())
        storage_path = f"{pdf_id}/{filename}"

        # Upload PDF
        supabase.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file_bytes,
            file_options={
                "content-type": "application/pdf"
            }
        )

        # Get public URL
        file_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)

        # Insert metadata into DB
        supabase.table("pdf_files").insert({
            "id": pdf_id,
            "file_name": filename,
            "file_url": file_url,
        }).execute()

        return {
            "pdf_id": pdf_id,
            "file_url": file_url,
            "url": file_url,
            "storage_path": storage_path
        }

    except Exception as e:
        raise RuntimeError(f"❌ Supabase PDF upload failed: {str(e)}")