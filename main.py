from fastapi import FastAPI
import ollama
import re
from rag.vectorstore import VectorStore
from rag.preprocess import load_slides, chunk_text

app = FastAPI()

# ======================================
# Initialize vector store
# ======================================
vs = VectorStore()
docs = load_slides("data")  # load PDFs from /data

for doc in docs:
    for chunk in chunk_text(doc["text"], chunk_size=200):
        vs.docs.append({
            "file": doc["file"],
            "text": chunk,
            "page": doc["page"]
        })

vs.fit()  # build TF–IDF vectors


# ======================================
# Ollama call
# ======================================
def ask_ollama(question: str, context: str) -> str:
    """Send query + context to Ollama for grounded answers."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant for RMIT students. "
                "Your job is to extract and present information clearly from the provided context. "
                "If the user asks for a summary, summarise the content into a clear, concise overview. "
                "If the context contains names, emails, roles, or assessment details, include them directly. "
                "Do not generalize — copy the details from the context when relevant. "
                "If the context does not contain enough information, reply exactly with: "
                "'The context does not provide this information.'"
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        }
    ]

    response = ollama.chat(
        model="gemma:2b",
        messages=messages
    )
    return response["message"]["content"]


# ======================================
# API endpoint
# ======================================
@app.post("/query")
async def query_api(request: dict):
    question = request.get("query", "")

    # Default retrieval
    retrieved = vs.search(question, top_k=7)

        # 🔍 Special rule: if user asks for summary of a week lecture
    week_match = re.search(r"week\s*0*(\d+)", question.lower())  # matches week 1, week01, etc.
    if "summary" in question.lower() or "summarise" in question.lower():
        if week_match:
            week_num = week_match.group(1)
            week_docs = [
                doc for doc in vs.docs
                if f"week{week_num}" in doc["file"].lower()
                or f"week0{week_num}" in doc["file"].lower()
            ]

            if week_docs:
                # Use *all* chunks from that week instead of TF-IDF subset
                retrieved = week_docs


    # Combine retrieved chunks
    context = "\n\n".join(
        [f"From {r['file']} (page {r['page']}): {r['text']}" for r in retrieved]
    )

    # Ask Ollama
    answer = ask_ollama(question, context)

    return {
        "answer": answer,
        "sources": retrieved
    }
