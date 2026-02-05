import uuid
import os
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue
)
from embedder import get_embeddings, get_embedding
from qdrant_client.models import PayloadSchemaType


COLLECTION_NAME = "pdf_chunks"

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# ------------------ COLLECTION ------------------
def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

        # 🔑 CREATE PAYLOAD INDEX FOR FILTERING
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="pdf_id",
            field_schema=PayloadSchemaType.KEYWORD
        )

# ------------------ STORE ------------------
def store_chunks_in_vector_db(chunks, metadatas):
    ensure_collection()
    embeddings = get_embeddings(chunks)

    points = []
    for i in range(len(chunks)):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embeddings[i],
                payload={
                    "text": chunks[i],
                    **metadatas[i]
                }
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)

# ------------------ QUERY ------------------
def query_similar_chunk_from_vector_db(question, pdf_id, top_k=3):
    ensure_collection()
    query_embedding = get_embedding(question)

    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="pdf_id",
                    match=MatchValue(value=pdf_id)
                )
            ]
        )
    )

    if not hits:
        return [], []

    docs = [hit.payload["text"] for hit in hits]
    metas = [
        {k: v for k, v in hit.payload.items() if k != "text"}
        for hit in hits
    ]

    return docs, metas

# ------------------ CLEAR ------------------
def clear_vector_db():
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
