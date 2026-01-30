# WaqediAI Reasoning Service

AI Reasoning microservice for the WaqediAI Enterprise Platform.

## Purpose

Provides citation-backed AI reasoning using an external LLM (Qwen via Ollama).

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reason` | POST | Execute AI reasoning on context |
| `/health` | GET | Liveness check |
| `/ready` | GET | Readiness check |

## Request Schema

```json
{
  "tenant_id": "uuid",
  "query": "What is the policy on...",
  "context_chunks": [
    {
      "chunk_id": "chunk_001",
      "document_id": "doc_001",
      "text": "The policy states that...",
      "language": "en"
    }
  ],
  "strategy": "qa"
}
```

## Response Schema

```json
{
  "answer": "According to the policy [chunk_001]...",
  "citations": [
    {"chunk_id": "chunk_001", "document_id": "doc_001"}
  ],
  "confidence": 0.85,
  "strategy": "qa",
  "model": "qwen2.5:7b"
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API endpoint |
| `OLLAMA_MODEL` | qwen2.5:7b | LLM model name |
| `OLLAMA_TIMEOUT` | 120 | Request timeout (seconds) |
| `PORT` | 8007 | Service port |

## Running

```bash
# Local development
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8007

# Docker
docker build -t reasoning-service .
docker run -p 8007:8007 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 reasoning-service
```

## Requirements

- Ollama running with Qwen model
- Python 3.11+
