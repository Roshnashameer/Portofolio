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
    {"role": "user", "content": "Tell me about her"},
    {"role": "assistant", "content": "Roshna N is a Full Stack Developer..."}
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

## Connecting the Frontend

The portfolio (`index.html`) works standalone with a client-side knowledge base. To connect it to this backend for real LLM-powered responses, add this before the chat script:

```html
<script>
  // Set this to enable backend-powered AI responses
  window.ASK_ROSHNA_API = "http://localhost:8000/ask";
</script>
```

When `window.ASK_ROSHNA_API` is set, the frontend will POST questions to the backend. When unset, it uses the built-in client-side RAG system.

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

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | OpenAI API key (optional, enables LLM responses) |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins |

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
