import os
from openai import OpenAI

# ------------------ CLIENT SETUP ------------------
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",   # required by OpenRouter
        "X-Title": "PDF-Chatbot"
    }
)

MODEL_NAME = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-3-4b-it:free"
)

# ------------------ BASIC ANSWER ------------------
def generate_answer(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ LLM Error: {str(e)}"


# ------------------ CONTEXT-AWARE QA ------------------
def generate_answer_with_context(question: str, context: str) -> str:
    prompt = (
        "You are a helpful assistant. Answer ONLY using the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )
    return generate_answer(prompt)


# ------------------ MAP-REDUCE SUMMARY ------------------
def map_reduce_summary(chunks, chunk_group_size=3):
    if not chunks:
        return "No content available to summarize."

    summaries = []

    for i in range(0, len(chunks), chunk_group_size):
        group = "\n\n".join(chunks[i:i + chunk_group_size])

        prompt = (
            "Summarize the following section of the document:\n\n"
            f"{group}"
        )

        summary = generate_answer(prompt)
        summaries.append(summary)

    final_prompt = (
        "Create a clear, concise, and complete final summary "
        "from the following partial summaries:\n\n"
        + "\n\n".join(summaries)
    )

    return generate_answer(final_prompt)