# Service Template

This directory contains the canonical service template for WaqediAI microservices.

## Usage

To create a new service, copy this template:

```powershell
Copy-Item -Recurse services/_template services/my-new-service
```

Then update:
1. `pyproject.toml` - Change the service name and description
2. `src/service_name/` - Rename to match your service
3. `Makefile` - Update the SERVICE_NAME variable
4. `README.md` - Document your service

## Structure

```
_template/
├── src/
│   └── service_name/
│       ├── __init__.py
│       ├── main.py          # FastAPI application
│       ├── config.py         # Service configuration
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py     # API endpoints
│       │   └── schemas.py    # Request/response models
│       ├── core/
│       │   ├── __init__.py
│       │   └── service.py    # Business logic
│       └── adapters/
│           ├── __init__.py
│           └── repository.py # External integrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── Dockerfile
├── pyproject.toml
├── Makefile
└── README.md
```

## Conventions

- All services use FastAPI
- Configuration via pydantic-settings
- Structured JSON logging
- Health and readiness endpoints at `/health` and `/ready`
- OpenAPI documentation at `/docs`
