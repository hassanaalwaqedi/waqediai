# WaqediAI Retrieval Service

Semantic search and vector retrieval for RAG pipeline.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/index` | POST | Index document chunks |
| `/search` | POST | Semantic search |
| `/delete` | POST | Delete document vectors |
| `/health` | GET | Health check |

## Index Request

```json
{
  "tenant_id": "uuid",
  "document_id": "doc_001",
  "chunks": [
    {"chunk_id": "c1", "text": "...", "language": "en"}
  ]
}
```

## Search Request

```json
{
  "tenant_id": "uuid",
  "query": "What is the policy...",
  "top_k": 5
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | localhost | Qdrant server |
| `QDRANT_PORT` | 6333 | Qdrant port |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Embedding model |
| `PORT` | 8006 | Service port |

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8006
```

## Requirements

- Qdrant running on port 6333
- Python 3.11+
