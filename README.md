# WaqediAI Enterprise Platform

An enterprise-grade, self-hosted AI knowledge and reasoning layer.

## Documentation

- [Phase 0: Strategic Foundation](./docs/architecture/phase-0-strategic-foundation.md)

## Repository Structure

```
waqediAI/
├── docs/           # Architecture, API docs, runbooks
├── services/       # Backend microservices (FastAPI)
├── libs/           # Shared Python libraries
├── clients/        # Flutter web and mobile clients
├── infra/          # Kubernetes, Docker, Terraform
├── tools/          # Scripts and generators
└── configs/        # Environment configurations
```

## Quick Start

```bash
# Setup development environment
./tools/scripts/setup-dev.ps1

# Run all services locally
docker-compose up -d

# Run a specific service
cd services/query-orchestrator
make dev
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI |
| Frontend | Flutter (Web + Mobile) |
| LLM | Qwen (primary), LLaMA (secondary) |
| Vector DB | Milvus / Qdrant |
| Message Queue | Apache Kafka |
| Database | PostgreSQL |
| Orchestration | Kubernetes |

## License

Proprietary - All Rights Reserved
