# WaqediAI Pipeline Service

Intelligent document ingestion & embedding pipeline.

## Pipeline Stages

```
Document → Extract → Normalize → Chunk → Embed → Store (Qdrant)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ingest` | POST | Ingest document (multipart) |
| `/delete` | POST | Delete document vectors |
| `/health` | GET | Health check |

## Supported Formats

- PDF (native & scanned)
- Images (PNG, JPG, JPEG)
- Text files (TXT, MD)

## Languages

- English (en)
- Arabic (ar)

## Usage

```bash
# Ingest a document
curl -X POST http://localhost:8008/ingest \
  -F "file=@document.pdf" \
  -F "tenant_id=00000000-0000-0000-0000-000000000001" \
  -F "document_id=doc_001"
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | localhost | Qdrant host |
| `QDRANT_PORT` | 6333 | Qdrant port |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Embedding model |

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8008
```
