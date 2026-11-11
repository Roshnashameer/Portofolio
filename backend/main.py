"""
Ask Roshna AI — FastAPI Backend
================================
A RAG-powered chat API that answers questions about Roshna N's portfolio.
Uses OpenAI for response generation with a local knowledge base for retrieval.

Setup:
  1. pip install -r requirements.txt
  2. export OPENAI_API_KEY="sk-..."
  3. uvicorn main:app --reload --port 8000

The frontend (index.html) can connect to this API by setting:
  window.ASK_ROSHNA_API = "http://localhost:8000/ask";
"""

import os
import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from knowledge_base import KNOWLEDGE_BASE, retrieve_context

app = FastAPI(title="Ask Roshna AI", version="1.0.0")

# CORS — allow the portfolio frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Initialize OpenAI client (optional — falls back to template responses)
openai_client = None
if OpenAI and os.getenv("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AskRequest(BaseModel):
    question: str
    history: Optional[list] = None  # [{"role": "user", "content": "..."}, ...]


class AskResponse(BaseModel):
    answer: str
    source: str  # "openai" or "local-rag"


SYSTEM_PROMPT = """You are Ask Roshna AI, a helpful assistant embedded in Roshna N's portfolio website.
Roshna N is a Full Stack Developer based in Kerala, India, with 3+ years of experience.
She works with Python, FastAPI, React, Node.js, TypeScript, and AWS, and builds AI-powered features with LLMs and RAG.

Answer questions about Roshna using ONLY the context provided below.
Be friendly, concise, and professional. Use bullet points where appropriate.
If the context doesn't contain the answer, say you don't have that information and suggest what you can help with.

Context from Roshna's knowledge base:
{context}
"""


@app.get("/")
def root():
    """Health check."""
    return {
        "status": "ok",
        "service": "Ask Roshna AI",
        "openai_enabled": openai_client is not None,
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """
    Answer a question about Roshna using RAG:
    1. Retrieve relevant context from the knowledge base
    2. Generate a response using OpenAI (if available) or local templates
    """
    # Step 1: Retrieve relevant context
    context_chunks = retrieve_context(req.question, top_k=3)

    if not context_chunks:
        return AskResponse(
            answer=(
                "I'm not sure about that one! I can answer questions about "
                "Roshna's projects, skills, experience, education, AI technologies, "
                "and contact info. Try asking about one of those topics!"
            ),
            source="local-rag",
        )

    context_text = "\n\n".join(context_chunks)

    # Step 2: Generate response
    if openai_client:
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT.format(context=context_text)},
            ]
            if req.history:
                messages.extend(req.history[-4:])  # last 2 turns
            messages.append({"role": "user", "content": req.question})

            response = openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            return AskResponse(
                answer=response.choices[0].message.content,
                source="openai",
            )
        except Exception as e:
            # Fall back to local RAG if OpenAI fails
            print(f"OpenAI error: {e}")

    # Fallback: local template-based response from retrieved context
    answer = generate_local_response(req.question, context_chunks)
    return AskResponse(answer=answer, source="local-rag")


def generate_local_response(question: str, chunks: list[str]) -> str:
    """Generate a response from retrieved context chunks (no LLM)."""
    # Join the retrieved chunks into a readable answer
    return "\n\n".join(chunks)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
