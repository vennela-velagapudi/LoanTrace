# LoanTrace

**Challenge**: Intain Campus FinTech Challenge 2026 — Full Stack Track
**Problem**: Loan Data Verification Copilot

LoanTrace is an AI-powered FinTech application designed to help Data Operators and Reviewers ingest, validate, and verify loan data from conflicting sources.

## Phase 1: Foundation (Current Status)
The project is currently in the Foundation phase.
*   **Frontend**: Next.js (App Router), Tailwind CSS, shadcn/ui.
*   **Backend**: FastAPI, SQLAlchemy, PostgreSQL.
*   **Auth**: JWT-based RBAC with three roles (Data Operator, Reviewer, Data Consumer).

## Local Development Setup

### Prerequisites
*   Docker & Docker Compose (for PostgreSQL)
*   Python 3.12+
*   Node.js 20+

### 1. Database Start
From the project root:
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv: `venv\Scripts\activate` on Windows or `source venv/bin/activate` on Mac/Linux
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
The frontend will be available at `http://localhost:3000`.

### Test Credentials
*   **Operator**: username: `operator`, password: `demo123`
*   **Reviewer**: username: `reviewer`, password: `demo123`
*   **Consumer**: username: `consumer`, password: `demo123`
