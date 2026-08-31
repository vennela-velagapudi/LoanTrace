# LoanTrace

**LoanTrace** is an AI-powered financial data quality and verification copilot built for the Intain Campus FinTech Challenge 2026. 

## The Problem
Financial institutions regularly ingest loan data from multiple, often conflicting sources. This raw data is frequently messy, incomplete, or logically inconsistent. Traditionally, resolving these discrepancies requires armies of analysts manually comparing spreadsheets, tracking emails, and updating central databases, leading to slow processing times, high operational costs, and unverifiable data provenance.

## The Solution
LoanTrace automates the ingestion, normalization, and deterministic validation of complex loan portfolios. When exceptions are flagged, the platform's **AI Review Assistant** (powered by Gemini) acts as a specialized copilot for human reviewers, explaining anomalies, comparing conflicting cross-source records, suggesting mathematical corrections, and generating professional resolution notes. Once a record is fully resolved, it is cryptographically hashed via SHA-256 and committed to an immutable verified ledger.

---

## Architecture & Tech Stack

### Frontend
*   **Framework**: Next.js (React) App Router
*   **Styling**: Tailwind CSS (Dark-first FinTech UI, Glassmorphism)
*   **Icons**: Lucide React

### Backend
*   **Framework**: FastAPI (Python)
*   **Database ORM**: SQLAlchemy & Alembic
*   **AI Integration**: Google GenAI SDK (`gemini-2.5-flash`)
*   **Security**: JWT Authentication, Server-Side RBAC, Pytest suite

### Core Workflows
1. **Data Ingestion**: Parses `loan_tape.csv` into a canonical schema while preserving raw JSON lineage.
2. **Validation Engine**: Deterministic Python rules engine executes schema, boundary, logic, and cross-source conflict checks.
3. **AI Copilot**: Gemini provides context-aware explanations, suggests corrections, and proposes natural language validation rules. Includes a graceful fallback mock for keyless demonstrations.
4. **Immutable Ledger**: Clean records are verified, hashed (SHA-256), and made available to downstream consumers.
5. **Audit Trail**: Every human and AI action triggers an append-only JSON-b audit event.

---

## Role-Based Access Control (RBAC)
The application enforces strict server-side and client-side routing based on three distinct roles:
*   **Data Operator** (`operator` / `demo123`): Responsible for uploading raw data batches and reviewing high-level validation results.
*   **Reviewer** (`reviewer` / `demo123`): Responsible for resolving exceptions, utilizing the AI Assistant, editing canonical data, and finalizing verification.
*   **Data Consumer** (`consumer` / `demo123`): Accesses the read-only Verified Ledger, data quality scores, complete audit trails, and exports CSVs.

---

## Local Development Setup (Examiner Guide)

### 1. Fresh Clone & Environment Variables
When you clone this repository, you start with a completely **clean** state. The local database will default to SQLite, and no transactional loan data is pre-seeded.

Create a `.env` file in the `backend/` directory by copying the provided example:
```bash
cd backend
copy .env.example .env
```

The `.env.example` file automatically defaults to a local SQLite database:
```env
DATABASE_URL=sqlite:///./local_schema.db
SECRET_KEY=YOUR_SUPER_SECRET_JWT_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:3000
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```
*(Note: If `GEMINI_API_KEY` is invalid or omitted, the AI Assistant gracefully degrades into a deterministic mock mode).*

### 2. Backend Setup & Database Migration
Set up a Python virtual environment, install dependencies, and run Alembic to create your fresh local SQLite database.

**On Windows:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\venv\Scripts\alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**On Mac/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000`.

### 4. Initialization and First Steps
The application starts with a completely **empty transactional database**. No records, exceptions, or verified data are pre-seeded.

**To populate the system as an Examiner:**
1. Login as the **Data Operator** (`operator` / `demo123`).
2. You will see an empty dashboard with zero loan/exception/verified records.
3. Use the upload panel to manually upload `data/loan_tape.csv`.
4. Only then does the system automatically ingest and validate the records, generating exceptions.
5. You can then log in as the **Reviewer** (`reviewer` / `demo123`) to resolve the exceptions using the AI Copilot.

### 5. Running Tests
The backend test suite is designed to test ingestion and verification:
```bash
cd backend
pytest tests/
```
