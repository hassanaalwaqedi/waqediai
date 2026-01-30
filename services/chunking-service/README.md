# WaqediAI Chunking Service

Semantic text chunking for Phase 5 Knowledge Processing.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chunk` | POST | Chunk document text |
| `/health` | GET | Health check |

## Strategies

- `semantic` - Sentence-boundary aware
- `paragraph` - Natural paragraph breaks
- `sliding_window` - Fixed size with overlap
- `sentence` - One sentence per chunk

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```
