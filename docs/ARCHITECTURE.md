# Architecture

## Overview

The platform converts Kubernetes architecture diagrams into validated YAML manifests using a simple three-tier layout:

1. **Frontend** (React + Vite) — user interface
2. **Auth Service** (FastAPI) — registration, login, JWT issuance
3. **AI Agent Service** (FastAPI) — diagram upload, manifest generation, validation

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth Service
    participant AI as AI Agent Service
    participant DB as PostgreSQL

    U->>F: Register / Login
    F->>A: POST /register or /login
    A->>DB: Persist user
    A-->>F: JWT access token
    U->>F: Upload diagram
    F->>AI: POST /upload-diagram (Bearer JWT)
    AI-->>F: file_id
    F->>AI: POST /generate-manifest
    AI-->>F: manifests + combined YAML
    F->>AI: POST /validate-manifest
    AI-->>F: validation report
    F->>AI: GET /download-manifest
    AI-->>F: YAML file
```

## Security

- Passwords hashed with bcrypt
- JWT signed with shared `JWT_SECRET_KEY`
- AI endpoints require valid Bearer token
- Manifest access scoped by user email in metadata

## LLM Modes

| Mode | When | Behavior |
|------|------|----------|
| Mock | `USE_MOCK_LLM=true` or no API key | Deterministic component inference |
| OpenAI | API key configured | LangChain + ChatOpenAI analysis |

## Validation Pipeline

1. YAML syntax (`PyYAML`)
2. kube-score (optional CLI)
3. kube-linter (optional CLI)
