import chromadb
import uuid
from embedder import get_embeddings, get_embedding

# ✅ New ChromaDB client setup
client = chromadb.PersistentClient(path="chroma_storage")
collection = client.get_or_create_collection(name="pdf_chunks")

def store_chunks_in_vector_db(chunks, metadatas):
    if not chunks:
        print("No chunks to store")
        return

    assert len(chunks) == len(metadatas), "Mismatch between chunks and metadata"

    ids = [str(uuid.uuid4()) for _ in chunks]

    embeddings = get_embeddings(chunks)

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    #print(f"✅ Stored {len(chunks)} chunks with metadata in vector DB")


def query_similar_chunk_from_vector_db(question, top_k=1):
    query_embedding = get_embedding(question)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    if result["documents"]:
        return result["documents"][0], result["metadatas"][0]
    else:
        return [], []

def get_all_chunks_from_db():
    results = collection.get(include=["documents"])
    return results["documents"]


def clear_vector_db():
# Get all items (IDs are always included by default)
    all_items = collection.get()
    all_ids = all_items["ids"]

    # Delete them all
    if all_ids:
        collection.delete(ids=all_ids)



def get_all_chunks_from_db():
    result = collection.get()
    return result.get("documents", [])
