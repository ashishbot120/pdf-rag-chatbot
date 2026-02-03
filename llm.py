import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL_NAME = "mistralai/mistral-7b-instruct"

def generate_answer(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"


def generate_answer_with_context(question: str, context: str) -> str:
    prompt = f"""
You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Answer:
"""
    return generate_answer(prompt)


def map_reduce_summary(chunks, chunk_group_size=3):
    if not chunks:
        return "No content available to summarize."

    summaries = []

    for i in range(0, len(chunks), chunk_group_size):
        group = "\n\n".join(chunks[i:i + chunk_group_size])
        prompt = f"Summarize the following part of the document:\n\n{group}"
        summaries.append(generate_answer(prompt))

    final_prompt = (
        "Create a final comprehensive summary from the following partial summaries:\n\n"
        + "\n\n".join(summaries)
    )

    return generate_answer(final_prompt)
