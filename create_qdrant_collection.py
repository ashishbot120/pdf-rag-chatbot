from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client.create_collection(
    collection_name="pdf_chunks",
    vectors_config=VectorParams(
        size=384,   # MUST match embedding model
        distance=Distance.COSINE
    )
)

print("✅ Qdrant collection created")
