# Ask Roshna AI — Backend

A RAG-powered chat API for the portfolio. Answers questions about Roshna N using a local knowledge base + OpenAI for response generation.

## Architecture

```
User Question
    │
    ▼
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Frontend     │────▶│  FastAPI /ask     │────▶│  OpenAI API  │
│  (index.html) │◀────│  + RAG retrieval  │◀────│  (gpt-4o-mini)│
└──────────────┘     └──────────────────┘     └─────────────┘
                            │
                     ┌──────▼──────┐
                     │ Knowledge   │
                     │ Base (local │
                     │ or vector   │
                     │  database)  │
                     └─────────────┘
```

**RAG flow:**

1. User asks a question (e.g., "What projects has Roshna worked on?")
2. Backend tokenizes the question and retrieves the most relevant knowledge base entries (keyword scoring)
3. Retrieved context + question are sent to OpenAI as a prompt
4. OpenAI generates a natural language answer using only the provided context
5. If OpenAI is unavailable, falls back to local template responses

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key-here"

# 3. Run the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### `GET /`

Health check — returns service status and whether OpenAI is enabled.

### `POST /ask`

Ask a question about Roshna.

**Request:**

```json
{
  "question": "What projects has Roshna worked on?",
  "history": [
    { "role": "user", "content": "Tell me about her" },
    { "role": "assistant", "content": "Roshna N is a Full Stack Developer..." }
  ]
}
```

**Response:**

```json
{
  "answer": "Roshna has worked on several projects:\n1. AI-Powered Risk Intelligence Platform...",
  "source": "openai"
}
```

The `source` field is `"openai"` when LLM is used, or `"local-rag"` when falling back to template responses.

### `POST /contact`

Handle contact form submissions from the portfolio.

**Request:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Job Opportunity",
  "message": "I'd like to discuss a full-stack position..."
}
```

**Response:**

```json
{
  "success": true,
  "message": "Message sent successfully! Roshna will get back to you soon."
}
```

**Email Configuration (Environment Variables):**

- `EMAIL_HOST` — SMTP server (e.g., `smtp.gmail.com`)
- `EMAIL_PORT` — SMTP port (e.g., `587` for TLS)
- `EMAIL_USER` — Email account to send from
- `EMAIL_PASSWORD` — Email password or app-specific password
- `EMAIL_TO` — Recipient email (defaults to `roshnasharaf123@gmail.com`)

**Gmail Setup:**

1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password at https://myaccount.google.com/apppasswords
3. Use these environment variables:
   ```bash
   export EMAIL_HOST="smtp.gmail.com"
   export EMAIL_PORT="587"
   export EMAIL_USER="your-email@gmail.com"
   export EMAIL_PASSWORD="your-app-specific-password"
   export EMAIL_TO="roshnasharaf123@gmail.com"
   ```

## Connecting the Frontend

The portfolio (`index.html`) works standalone with a client-side knowledge base. To connect it to this backend for real LLM-powered responses and contact form handling, add this before the scripts:

```html
<script>
  // Set this to enable backend-powered AI responses
  window.ASK_ROSHNA_API = "http://localhost:8000/ask";

  // Set this to enable backend-powered contact form
  window.CONTACT_API = "http://localhost:8000/contact";
</script>
```

When these variables are set, the frontend will POST to the backend. When unset:

- AI chat uses the built-in client-side RAG system
- Contact form shows an error message and prompts users to email directly

## Upgrading to a Vector Database

The current `knowledge_base.py` uses keyword overlap for retrieval. To use a real vector database:

### Option 1: ChromaDB (local, free)

```bash
pip install chromadb
```

```python
import chromadb

client = chromadb.PersistentClient()
collection = client.create_collection("roshna_kb")

# Index the knowledge base
for entry in KNOWLEDGE_BASE:
    collection.add(
        documents=[entry["content"]],
        metadatas=[{"id": entry["id"]}],
        ids=[entry["id"]]
    )

# Query
results = collection.query(query_texts=[question], n_results=3)
```

### Option 2: Pinecone (managed, cloud)

```bash
pip install pinecone-client
```

### Option 3: pgvector (PostgreSQL extension)

```bash
pip install psycopg[binary] pgvector
```

## Environment Variables

| Variable          | Default                     | Description                                      |
| ----------------- | --------------------------- | ------------------------------------------------ |
| `OPENAI_API_KEY`  | —                           | OpenAI API key (optional, enables LLM responses) |
| `OPENAI_MODEL`    | `gpt-4o-mini`               | OpenAI model to use                              |
| `ALLOWED_ORIGINS` | `*`                         | Comma-separated CORS origins                     |
| `EMAIL_HOST`      | —                           | SMTP server (e.g., `smtp.gmail.com`)             |
| `EMAIL_PORT`      | `587`                       | SMTP port                                        |
| `EMAIL_USER`      | —                           | Email account to send from                       |
| `EMAIL_PASSWORD`  | —                           | Email password or app-specific password          |
| `EMAIL_TO`        | `roshnasharaf123@gmail.com` | Recipient email for contact form                 |

## Deployment

### Vercel Serverless

Create `api/ask.py` using Vercel's Python runtime with the same FastAPI app.

### Railway / Render

Deploy this folder directly. Set `OPENAI_API_KEY` as an environment variable.

### Docker

```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
