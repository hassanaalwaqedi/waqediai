# WaqediAI Advanced RAG Service

Citation-backed AI reasoning engine.

## Pipeline

```
Query → Understand → Retrieve → Rank → Prompt → Generate → Cite
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | Execute RAG query |
| `/health` | GET | Health check |

## Request

```json
{
  "tenant_id": "uuid",
  "query": "What is the company policy on...",
  "top_k": 5,
  "conversation_id": "optional"
}
```

## Response

```json
{
  "answer": "According to the policy [chunk_xxx]...",
  "citations": [
    {"chunk_id": "chunk_xxx", "document_id": "doc_001", "text_excerpt": "..."}
  ],
  "confidence": 0.85,
  "answer_type": "direct",
  "language": "en"
}
```

## Features

- Arabic & English support
- Citation enforcement
- Intent classification
- Conversation context
- Diversity reranking
- Audit logging

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8009
```

## Requirements

- Qdrant on port 6333
- Ollama with Qwen model
