import ollama
import json

def generate_answer(prompt: str, model: str = "mistral") -> str:
    """
    Generate answer using Ollama
    """
    try:
        response = ollama.chat(
            model=model,   
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error generating response: {str(e)}. Make sure Ollama is running and the model '{model}' is installed."

def generate_answer_with_context(question: str, context: str, model: str = "mistral") -> str:
    """
    Generate answer with specific context formatting
    """
    prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer based only on the information provided in the context
- If the answer is not in the context, say "I cannot find this information in the provided context"
- Be concise but complete
- Use specific details from the context when possible

Answer:"""
    
    return generate_answer(prompt, model)

from llm import generate_answer  # Make sure this exists

def map_reduce_summary(chunks, chunk_group_size=3):
    """
    Generate a concise summary by summarizing small groups of chunks,
    and then summarizing those partial summaries.
    """
    if not chunks:
        return "No content available to summarize."

    summaries = []

    # Phase 1: Map step - summarize groups of chunks
    for i in range(0, len(chunks), chunk_group_size):
        group = "\n\n".join(chunks[i:i + chunk_group_size])
        prompt = f"Summarize the following part of the document:\n\n{group}"
        summary = generate_answer(prompt)
        summaries.append(summary)

    # Phase 2: Reduce step - summarize the summaries
    combined_summary = "\n\n".join(summaries)
    final_prompt = f"Create a final comprehensive summary from the following partial summaries:\n\n{combined_summary}"
    final_summary = generate_answer(final_prompt)

    return final_summary



