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
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = ""
    message: str


class ContactResponse(BaseModel):
    success: bool
    message: str


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


@app.post("/contact", response_model=ContactResponse)
def contact(req: ContactRequest):
    """
    Handle contact form submissions.
    Sends email notification to Roshna and optionally to the sender.
    
    Required environment variables:
    - EMAIL_HOST: SMTP server (e.g., smtp.gmail.com)
    - EMAIL_PORT: SMTP port (e.g., 587 for TLS)
    - EMAIL_USER: Email account to send from
    - EMAIL_PASSWORD: Email password or app password
    - EMAIL_TO: Recipient email (Roshna's email)
    """
    try:
        # Get email configuration from environment
        email_host = os.getenv("EMAIL_HOST")
        email_port = int(os.getenv("EMAIL_PORT", "587"))
        email_user = os.getenv("EMAIL_USER")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_to = os.getenv("EMAIL_TO", "roshnasharaf123@gmail.com")
        
        if not all([email_host, email_user, email_password]):
            # If email not configured, just log it
            print(f"Contact form submission (email not configured):")
            print(f"From: {req.name} <{req.email}>")
            print(f"Subject: {req.subject}")
            print(f"Message: {req.message}")
            return ContactResponse(
                success=True,
                message="Message received! (Email service not configured)"
            )
        
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Portfolio Contact: {req.subject or 'New Message'}"
        msg["From"] = email_user
        msg["To"] = email_to
        msg["Reply-To"] = req.email
        
        # Email body
        text_content = f"""
New contact form submission from your portfolio:

Name: {req.name}
Email: {req.email}
Subject: {req.subject or "(no subject)"}

Message:
{req.message}

---
This email was sent from your portfolio contact form.
"""
        
        html_content = f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #0f766e;">New Portfolio Contact</h2>
    <table style="border-collapse: collapse; margin: 20px 0;">
      <tr>
        <td style="padding: 8px; font-weight: bold;">Name:</td>
        <td style="padding: 8px;">{req.name}</td>
      </tr>
      <tr>
        <td style="padding: 8px; font-weight: bold;">Email:</td>
        <td style="padding: 8px;"><a href="mailto:{req.email}">{req.email}</a></td>
      </tr>
      <tr>
        <td style="padding: 8px; font-weight: bold;">Subject:</td>
        <td style="padding: 8px;">{req.subject or "(no subject)"}</td>
      </tr>
    </table>
    <div style="background-color: #f7f8fa; padding: 15px; border-left: 4px solid #0f766e; margin: 20px 0;">
      <h3 style="margin-top: 0;">Message:</h3>
      <p>{req.message.replace(chr(10), '<br>')}</p>
    </div>
    <hr style="border: none; border-top: 1px solid #e2e6ec; margin: 30px 0;">
    <p style="color: #999; font-size: 12px;">This email was sent from your portfolio contact form.</p>
  </body>
</html>
"""
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(email_host, email_port) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
        
        return ContactResponse(
            success=True,
            message="Message sent successfully! Roshna will get back to you soon."
        )
        
    except Exception as e:
        print(f"Error sending contact form email: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send message. Please try emailing directly."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
