from sentence_transformers import SentenceTransformer
import numpy as np

# Initialize model globally
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    MODEL_LOADED = True
except Exception as e:
    print(f"Error loading embedding model: {e}")
    MODEL_LOADED = False
    model = None

def get_embedding(text: str) -> list:
    """
    Get embedding for a single text
    """
    if not MODEL_LOADED:
        raise Exception("Embedding model not loaded. Install sentence-transformers.")
    
    if not text or not text.strip():
        # Return zero vector for empty text
        return [0.0] * 384  # all-MiniLM-L6-v2 has 384 dimensions
    
    try:
        embedding = model.encode([text.strip()])[0]
        return embedding.tolist()
    except Exception as e:
        raise Exception(f"Error generating embedding: {e}")

def get_embeddings(chunks: list[str]) -> list:
    """
    Get embeddings for multiple texts
    """
    if not MODEL_LOADED:
        raise Exception("Embedding model not loaded. Install sentence-transformers.")
    
    if not chunks:
        return []
    
    # Filter out empty chunks
    valid_chunks = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]
    
    if not valid_chunks:
        return []
    
    try:
        embeddings = model.encode(valid_chunks)
        return embeddings.tolist()
    except Exception as e:
        raise Exception(f"Error generating embeddings: {e}")

def check_model_loaded() -> bool:
    """
    Check if the embedding model is properly loaded
    """
    return MODEL_LOADED

def get_model_info() -> dict:
    """
    Get information about the loaded model
    """
    if not MODEL_LOADED:
        return {"loaded": False, "error": "Model not loaded"}
    
    return {
        "loaded": True,
        "model_name": "all-MiniLM-L6-v2",
        "dimensions": 384,
        "max_sequence_length": model.max_seq_length
    }