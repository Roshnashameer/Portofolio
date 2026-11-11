"""
Knowledge Base for Ask Roshna AI
=================================
Structured data about Roshna N's portfolio for RAG retrieval.
Each entry has keywords for matching and content for the LLM context.

To upgrade to a real vector database (e.g., ChromaDB, Pinecone, pgvector):
1. Convert each entry's 'content' into an embedding via OpenAI embeddings API
2. Store embeddings in your vector DB
3. Replace retrieve_context() with a similarity search against the vector DB
"""

import re
from typing import List

KNOWLEDGE_BASE = [
    {
        "id": "about",
        "keywords": ["about", "who", "roshna", "bio", "background", "developer", "person", "herself", "introduce"],
        "content": (
            "Roshna N is a Full Stack Developer based in Kerala, India, with 3+ years of experience. "
            "She builds both sides of an application — REST APIs and databases on the backend, "
            "React interfaces on the front end — and ships on AWS. "
            "She's currently a UI Developer at SwarmLens Inc, working on an AI-powered risk "
            "intelligence platform with LLMs and RAG. Her M.Sc. in Data Science gives her a strong "
            "foundation for building AI-driven products."
        ),
    },
    {
        "id": "projects",
        "keywords": ["project", "projects", "work", "built", "portfolio", "showcase", "made", "created", "developed", "application", "app"],
        "content": (
            "Projects Roshna has worked on:\n"
            "1. AI-Powered Risk Intelligence Platform — React + TypeScript interfaces with AI chat "
            "built on Generative AI, RAG and LLM workflows. APIs provide contextual risk insights.\n"
            "2. Sharon Pipes Reward Program — A full-stack rewards app. Roshna led the backend: "
            "reward/membership workflows, Cashfree payment integration, AWS-based OCR receipt scanning. "
            "Stack: React, Node.js, MongoDB, AWS.\n"
            "3. Malayalam-English Code-Mixed Data Analysis — A Python NLP notebook analysing "
            "code-mixed text. Available on GitHub.\n"
            "4. Profile Data Scraping — A Python notebook for collecting and processing profile data. "
            "Available on GitHub."
        ),
    },
    {
        "id": "risk-platform",
        "keywords": ["risk", "intelligence", "swarmlens", "ai chat", "rag", "llm", "generative"],
        "content": (
            "At SwarmLens Inc, Roshna works on an AI-Powered Risk Intelligence Platform. "
            "She integrates FastAPI REST APIs, LLM services and RAG workflows into AI chat "
            "interfaces and risk-analysis experiences. The frontend is built with React and "
            "TypeScript. The platform provides contextual risk insights and recommendations "
            "using Generative AI."
        ),
    },
    {
        "id": "sharon-pipes",
        "keywords": ["sharon", "pipes", "reward", "cashfree", "ocr", "membership", "faircode", "client"],
        "content": (
            "The Sharon Pipes Reward Program was built at Faircode Technologies. Roshna led the "
            "backend: reward and membership workflows with MongoDB, Express, React and Node.js "
            "(MERN stack), Cashfree payment gateway integration, AWS-based OCR receipt scanning "
            "for automated receipt processing, third-party service integrations and performance "
            "optimization."
        ),
    },
    {
        "id": "react",
        "keywords": ["react", "frontend", "component", "components", "ui", "interface", "typescript", "tsx", "hook"],
        "content": (
            "Roshna has strong React experience (88% proficiency). She builds reusable React "
            "components with TypeScript, AI chat interfaces and risk-analysis dashboards at "
            "SwarmLens, and full-stack MERN application frontends at Faircode Technologies. "
            "You can see her React work in the AI-Powered Risk Intelligence Platform and the "
            "Sharon Pipes Reward Program."
        ),
    },
    {
        "id": "python-fastapi",
        "keywords": ["python", "fastapi", "api", "apis", "rest", "backend", "server", "endpoint", "py"],
        "content": (
            "Yes, Roshna has strong Python and FastAPI experience (90% proficiency). She uses "
            "FastAPI for building REST APIs at SwarmLens Inc, Python for NLP and data analysis "
            "projects, and AI/ML integration with Python (LLM services, RAG pipelines). "
            "She's comfortable with both Python/FastAPI and Node.js/Express for backend development."
        ),
    },
    {
        "id": "node-mern",
        "keywords": ["node", "nodejs", "express", "mern", "mongodb", "javascript", "backend", "fullstack", "full stack"],
        "content": (
            "Roshna has 3+ years of full-stack experience with the MERN stack (MongoDB, "
            "Express.js, React.js, Node.js). At Faircode Technologies she was the backend lead "
            "on the Sharon Pipes Reward Program, building REST APIs, database workflows, and "
            "third-party integrations including Cashfree payments and AWS OCR services."
        ),
    },
    {
        "id": "ai-tech",
        "keywords": ["ai", "artificial", "intelligence", "llm", "rag", "generative", "machine", "learning", "ml", "model", "agent", "prompt", "chatgpt", "openai"],
        "content": (
            "Roshna has hands-on AI technology experience: LLM integration (building AI chat "
            "interfaces with large language models), RAG pipelines (retrieval-augmented "
            "generation for contextual AI responses), multi-agent systems, prompt engineering, "
            "and AI chat apps. Her M.Sc. in Data Science gives her a strong theoretical foundation. "
            "She's certified in TensorFlow and Google Cloud ML."
        ),
    },
    {
        "id": "experience",
        "keywords": ["experience", "work", "job", "jobs", "career", "company", "companies", "role", "roles", "employed", "history", "years"],
        "content": (
            "Roshna has 3+ years of professional experience:\n"
            "1. UI Developer at SwarmLens Inc (Jan 2026 – Present) — AI-powered risk intelligence "
            "platform with React, TypeScript, FastAPI and LLM/RAG workflows.\n"
            "2. MERN Stack Developer at Faircode Technologies (Mar 2024 – Jan 2026, Kochi) — "
            "Backend lead on Sharon Pipes Reward Program. Full-stack MERN, AWS, Docker, CI/CD.\n"
            "3. MERN Stack Developer at Luminar Technolab (Jun 2023 – Jan 2024) — MERN stack development."
        ),
    },
    {
        "id": "skills",
        "keywords": ["skill", "skills", "tech", "technology", "technologies", "tools", "stack", "know", "languages", "framework"],
        "content": (
            "Roshna's technical skills:\n"
            "- Languages: Python (90%), JavaScript/TypeScript (85%)\n"
            "- Backend & APIs: FastAPI (90%), Node.js/Express (85%), REST APIs, third-party integrations\n"
            "- Frontend: React.js (88%), TypeScript, reusable components\n"
            "- Databases: MongoDB (90%), PostgreSQL/MySQL (80%)\n"
            "- AWS & DevOps: Lambda, S3, EC2 (82%), Docker, CI/CD, Git (80%)\n"
            "- AI Applications: LLM integration, RAG pipelines, multi-agent systems, prompt engineering"
        ),
    },
    {
        "id": "education",
        "keywords": ["education", "degree", "university", "college", "study", "studied", "qualification", "academic", "kerala"],
        "content": (
            "Roshna's education: M.Sc. in Data Science from University of Kerala (2019-2021), "
            "B.Sc. in Computer Science from University of Kerala (2013-2016). "
            "Certifications: TensorFlow for AI/ML/DL, Google Compute Engine Specialization, "
            "Google Cloud Data Engineering with ML APIs."
        ),
    },
    {
        "id": "contact",
        "keywords": ["contact", "email", "reach", "linkedin", "github", "hire", "available", "phone", "connect", "social", "message"],
        "content": (
            "You can reach Roshna via email at roshnasharaf123@gmail.com, LinkedIn at "
            "linkedin.com/in/roshna-n-3b8b00120, or GitHub at github.com/Roshnashameer. "
            "She's based in Kerala, India and is open to Full Stack (Python / MERN), "
            "Node.js and React roles."
        ),
    },
    {
        "id": "availability",
        "keywords": ["available", "hire", "hiring", "open", "looking", "job", "seeking", "freelance", "position"],
        "content": (
            "Yes, Roshna is open to Full Stack (Python / MERN), Node.js and React roles. "
            "She's available for hire and can be reached via email at roshnasharaf123@gmail.com "
            "or LinkedIn at linkedin.com/in/roshna-n-3b8b00120."
        ),
    },
    {
        "id": "aws-devops",
        "keywords": ["aws", "cloud", "docker", "devops", "ci", "cd", "pipeline", "deploy", "deployment", "lambda", "s3", "ec2", "infrastructure"],
        "content": (
            "Roshna has solid AWS and DevOps experience (82%): AWS Lambda, S3, EC2 for "
            "serverless functions, storage and compute; Docker for containerization; CI/CD "
            "pipelines for automated deployment; AWS-based OCR and AI automation services. "
            "She deployed the Sharon Pipes Reward Program using AWS, Docker, Git and CI/CD workflows."
        ),
    },
]

# Simple stop words for keyword matching
STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should", "can",
    "of", "in", "on", "at", "to", "for", "with", "from", "by", "as", "about",
    "and", "or", "but", "not", "if", "when", "where", "why", "how", "what",
    "which", "who", "i", "you", "he", "she", "it", "we", "they", "my", "your",
}


def tokenize(query: str) -> List[str]:
    """Tokenize a query into meaningful keywords."""
    tokens = re.sub(r"[^a-z0-9\s+#]", " ", query.lower()).split()
    return [t for t in tokens if len(t) > 1 and t not in STOP_WORDS]


def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """
    Retrieve the most relevant knowledge base entries for a query.
    Uses keyword overlap scoring (simplified RAG retrieval step).

    To upgrade to vector database:
    1. Generate embedding: emb = openai.embeddings.create(input=query, model="text-embedding-3-small")
    2. Search vector DB: results = vector_db.similarity_search(emb, top_k=top_k)
    3. Return results
    """
    tokens = tokenize(query)
    if not tokens:
        return []

    scored = []
    for entry in KNOWLEDGE_BASE:
        score = 0
        for token in tokens:
            for keyword in entry["keywords"]:
                if keyword == token:
                    score += 3
                elif keyword in token or token in keyword:
                    score += 1
        if score > 0:
            scored.append((score, entry["content"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [content for _, content in scored[:top_k]]
