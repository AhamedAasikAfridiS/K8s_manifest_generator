# AI-Powered Kubernetes Architecture Diagram to Manifest Generator

A production-style web platform that uploads Kubernetes architecture diagrams, analyzes components with AI (or a deterministic mock mode), generates multi-resource YAML manifests, validates them, and lets users download deployment-ready files.

## Project Overview

| Capability | Description |
|------------|-------------|
| Diagram upload | PNG, JPEG, WEBP, GIF, PDF |
| Component detection | Deployment, Service, Ingress, ConfigMap, Namespace, HPA |
| Manifest generation | Structured YAML per resource + combined bundle |
| Validation | YAML syntax, kube-score, kube-linter |
| Authentication | JWT-based register/login |
| Deployment | Docker Compose + Kubernetes manifests |

## Architecture

```
┌─────────────┐     JWT      ┌──────────────────┐
│   Frontend  │─────────────▶│   Auth Service   │──▶ PostgreSQL
│  React/Vite │              │    FastAPI       │
└──────┬──────┘              └──────────────────┘
       │ JWT
       ▼
┌──────────────────┐
│  AI Agent Service│──▶ uploads/ + generated/
│     FastAPI      │──▶ OpenAI (optional) / Mock LLM
└──────────────────┘
```

**Microservices (practical layout):**

1. **Frontend** — React SPA (not a backend microservice, but a deployable UI tier)
2. **Auth Service** — user accounts and JWT
3. **AI Agent Service** — diagram processing, manifest generation, validation

No API gateway, service mesh, or message broker — direct HTTP integration for stability and simpler operations.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for sequence diagrams and security notes.

## Folder Structure

```
cloud_capstone_project/
├── frontend/                 # React + Vite + Tailwind UI
├── authservice/              # Auth microservice (FastAPI)
├── ai-agent-service/         # AI/manifest microservice (FastAPI)
├── kubernetes/               # K8s deployment manifests
├── manifests/                # Sample generated YAML output
├── docs/                     # Architecture documentation
├── scripts/                  # Setup and test automation
├── docker/                   # Docker-related notes
├── tests/                    # Python unit tests
├── docker-compose.yml        # Local full-stack deployment
├── .env.example              # Root compose variables
└── README.md
```

## Prerequisites

- **Docker Desktop** (recommended) with Docker Compose v2
- **Node.js 20+** (optional, for local frontend dev)
- **Python 3.12+** (optional, for local API dev / tests)
- **Git**

## Environment Variable Setup

Each service uses its own `.env` file. Run the setup script to copy examples:

**Windows (PowerShell):**

```powershell
.\scripts\setup-env.ps1
```

**Linux/macOS:**

```bash
chmod +x scripts/*.sh
./scripts/setup-env.sh
```

### Root `.env` (Docker Compose)

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Database user |
| `POSTGRES_PASSWORD` | Database password |
| `POSTGRES_DB` | Database name |
| `JWT_SECRET_KEY` | Shared secret for auth + AI services |
| `USE_MOCK_LLM` | `true` = no OpenAI key required |
| `OPENAI_API_KEY` | OpenAI key when using real LLM |

### Auth Service (`authservice/.env`)

| Variable | Default |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Must match root/AI service |
| `PORT` | `8001` |
| `CORS_ORIGINS` | Frontend URLs |

### AI Agent Service (`ai-agent-service/.env`)

| Variable | Default |
|----------|---------|
| `JWT_SECRET_KEY` | Must match auth service |
| `USE_MOCK_LLM` | `true` |
| `OPENAI_API_KEY` | Optional |
| `PORT` | `8002` |

### Frontend (`frontend/.env`)

| Variable | Default |
|----------|---------|
| `VITE_AUTH_API_URL` | `http://localhost:8001` |
| `VITE_AI_API_URL` | `http://localhost:8002` |

> **Important:** `JWT_SECRET_KEY` must be identical in auth and AI agent services.

## Docker Setup (Recommended)

### 1. Prepare environment files

```powershell
.\scripts\setup-env.ps1
```

Edit `.env`, `authservice/.env`, and `ai-agent-service/.env` if needed.

### 2. Start all services

```powershell
docker compose up --build -d
```

Or use the helper script (Git Bash/WSL):

```bash
./scripts/start-local.sh
```

### 3. Access services

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Auth API docs | http://localhost:8001/docs |
| AI Agent API docs | http://localhost:8002/docs |
| PostgreSQL | localhost:5432 |

### 4. Stop services

```powershell
docker compose down
```

## Run Locally (Without Docker)

### PostgreSQL

Run PostgreSQL 16 and create database `k8s_auth_db` with user/password from `.env.example`.

### Auth Service

```powershell
cd authservice
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8001
```

### AI Agent Service

```powershell
cd ai-agent-service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8002
```

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

## How to Test APIs

### Swagger UI

- Auth: http://localhost:8001/docs
- AI Agent: http://localhost:8002/docs (authorize with Bearer token from login)

### Automated script (Bash)

```bash
./scripts/test-apis.sh
```

### Manual curl example

```bash
# Register
curl -X POST http://localhost:8001/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"devops","password":"SecurePass123"}'

# Login
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'

# Upload (replace TOKEN)
curl -X POST http://localhost:8002/upload-diagram \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@diagram.png"
```

## Frontend Usage Guide

1. **Register** at `/register` or **Login** at `/login`
2. Open **Dashboard** — verify Auth and AI service health
3. Go to **Upload** — select architecture diagram, set namespace/app name
4. Click **Upload & Generate** — redirects to **Manifest Viewer**
5. Review per-file YAML and **Download YAML**
6. Open **Validation** — run kube-score/linter checks on latest manifest

### UI Theme

Yellow (`#f5c518`) + black DevOps dashboard styling via TailwindCSS.

## API Endpoints

### Auth Service (port 8001)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create account + JWT |
| POST | `/login` | Authenticate + JWT |
| GET | `/health` | Service + DB health |

### AI Agent Service (port 8002)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/upload-diagram` | Yes | Upload diagram image |
| POST | `/generate-manifest` | Yes | Generate K8s YAML |
| POST | `/validate-manifest` | Yes | Validate YAML |
| GET | `/download-manifest` | Yes | Download combined YAML |
| GET | `/health` | No | Service health + LLM mode |

## Running Unit Tests

```powershell
cd tests
pip install -r requirements.txt
pip install -r ../ai-agent-service/requirements.txt
pytest -v
```

## Kubernetes Deployment

1. Build and tag images:

```bash
docker build -t k8s-manifest-generator/auth-service:latest ./authservice
docker build -t k8s-manifest-generator/ai-agent-service:latest ./ai-agent-service
docker build -t k8s-manifest-generator/frontend:latest ./frontend
```

2. Update secrets in `kubernetes/postgres.yaml` and `kubernetes/auth-service.yaml`

3. Apply manifests:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/auth-service.yaml
kubectl apply -f kubernetes/ai-agent-service.yaml
kubectl apply -f kubernetes/frontend.yaml
```

## Common Troubleshooting

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` on AI endpoints | Login again; ensure `JWT_SECRET_KEY` matches in both backend `.env` files |
| Auth service won't start | Wait for Postgres healthcheck; verify `DATABASE_URL` |
| CORS errors | Add your frontend URL to `CORS_ORIGINS` in both backend services |
| Empty manifest page | Upload and generate first; check browser sessionStorage |
| kube-score/linter skipped | Tools may be missing locally; syntax validation still runs |
| OpenAI errors | Set `USE_MOCK_LLM=true` or provide valid `OPENAI_API_KEY` |
| Frontend can't reach APIs | Use `VITE_*` URLs reachable from browser (localhost, not docker internal names) |

### Docker-specific

```powershell
docker compose logs -f auth-service
docker compose logs -f ai-agent-service
docker compose ps
```

Rebuild after code changes:

```powershell
docker compose up --build -d
```

## Production Deployment Considerations

- Replace `JWT_SECRET_KEY` with a strong random value (32+ chars)
- Use managed PostgreSQL (RDS, Cloud SQL, Azure Database)
- Store `OPENAI_API_KEY` in a secrets manager
- Enable HTTPS via ingress/reverse proxy
- Use persistent volumes for AI uploads/generated manifests
- Configure resource limits and HPA on all deployments
- Centralize logging (ELK, CloudWatch, Loki)
- Add rate limiting on upload endpoints
- Scan container images in CI/CD

## Future Enhancements

- Helm chart packaging
- Multi-diagram project workspaces
- GitOps export (Argo CD / Flux application manifests)
- Vision model image analysis (GPT-4 Vision)
- RBAC and team accounts
- Manifest diff and versioning
- CI pipeline template generation

## License

MIT — suitable for capstone and portfolio use.
