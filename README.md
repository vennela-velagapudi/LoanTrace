# LoanTrace

**Challenge**: Intain Campus FinTech Challenge 2026 — Full Stack Track
**Problem**: Loan Data Verification Copilot

LoanTrace is an AI-powered FinTech application designed to help Data Operators and Reviewers ingest, validate, and verify loan data from conflicting sources.

## Phase 3: Exception Workflow & Audit Trail (Current Status)
The project has completed Phase 3.
*   **Data Foundation**: Capable of generating deterministic synthetic loan data with intentional anomalies.
*   **Ingestion Pipeline**: Upload endpoint parses CSV files, preserves raw lineage, and attempts schema normalization.
*   **Validation Engine**: A deterministic Python rules engine executes configurable data quality and cross-source checks.
*   **Reviewer Workflow**: Reviewers can review queue items, patch canonical data safely, and approve/reject/request correction.
*   **Audit Trail**: Highly secure append-only audit trail implemented for all mutations.
*   **Authentication**: Frontend fully wired to FastAPI backend utilizing JWT and RBAC.

## Local Development Setup

### Prerequisites
*   Docker & Docker Compose (for PostgreSQL)
*   Python 3.12+
*   Node.js 20+

### 0. Generate Synthetic Data
```bash
python scripts/generate_synthetic_data.py
```
This generates `data/loan_tape.csv`, `servicer_update.csv`, and others with deterministic 2,000+ records containing specific anomalies (negative balances, missing IDs, conflicting tape/servicer data).

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
