# LoanTrace 🏦✨

**LoanTrace** is an AI-powered financial data quality and verification copilot built for the Intain Campus FinTech Challenge 2026. 

## The Problem
Financial institutions regularly ingest loan data from multiple, often conflicting sources (e.g., originators, servicers, and document repositories). This raw data is frequently messy, incomplete, or logically inconsistent. Traditionally, resolving these discrepancies requires armies of analysts manually comparing spreadsheets, tracking emails, and updating central databases, leading to slow processing times, high operational costs, and unverifiable data provenance.

## The Solution
LoanTrace automates the ingestion, normalization, and deterministic validation of complex loan portfolios. When exceptions are flagged, the platform's **AI Review Assistant** (powered by Gemini) acts as a specialized copilot for human reviewers, explaining anomalies, comparing conflicting cross-source records, suggesting mathematical corrections, and generating professional resolution notes. Once a record is fully resolved, it is cryptographically hashed via SHA-256 and committed to an immutable verified ledger.

---

## 🏛️ Architecture & Tech Stack

### Frontend
*   **Framework**: Next.js (React) App Router
*   **Styling**: Tailwind CSS (Dark-first FinTech UI, Glassmorphism)
*   **Icons**: Lucide React
*   **Deployment**: Ready for Vercel

### Backend
*   **Framework**: FastAPI (Python)
*   **Database ORM**: SQLAlchemy & Alembic
*   **AI Integration**: Google GenAI SDK (`gemini-2.5-flash`)
*   **Security**: JWT Authentication, Server-Side RBAC, Pytest suite
*   **Deployment**: Ready for Render / AWS

### Core Workflows
1. **Data Ingestion**: Parses `loan_tape.csv`, `servicer_update.csv`, and `document_manifest.csv` into a canonical schema while preserving raw JSON lineage.
2. **Validation Engine**: Deterministic Python rules engine executes schema, boundary, logic, and cross-source conflict checks.
3. **AI Copilot**: Gemini provides context-aware explanations, suggests corrections, and proposes natural language validation rules. Includes a graceful fallback mock for keyless demonstrations.
4. **Immutable Ledger**: Clean records are verified, hashed (SHA-256), and made available to downstream consumers.
5. **Audit Trail**: Every human and AI action triggers an append-only JSON-b audit event.

---

## 👥 Role-Based Access Control (RBAC)
The application enforces strict server-side and client-side routing based on three distinct roles:
*   **Data Operator** (`operator` / `demo123`): Responsible for uploading raw data batches and reviewing high-level validation results.
*   **Reviewer** (`reviewer` / `demo123`): Responsible for resolving exceptions, utilizing the AI Assistant, editing canonical data, and finalizing verification.
*   **Data Consumer** (`consumer` / `demo123`): Accesses the read-only Verified Ledger, data quality scores, complete audit trails, and exports CSVs.

---

## 🚀 Local Development Setup

### 1. Environment Variables
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=sqlite:///./local_schema.db
# For production PostgreSQL: DATABASE_URL=postgresql://postgres:password@localhost:5432/loantrace

SECRET_KEY=YOUR_SUPER_SECRET_JWT_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:3000
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If `GEMINI_API_KEY` is omitted, the AI Assistant gracefully degrades into a deterministic mock mode suitable for offline demos).*

Create a `.env` file in the `frontend/` directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Generate Synthetic Demo Data
Generate a deterministic dataset with intentional financial anomalies (2,000+ records):
```bash
python scripts/generate_synthetic_data.py
```
This populates the `data/` folder with `loan_tape.csv`, `servicer_update.csv`, and `document_manifest.csv`.

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:3000`.

### 5. Running Tests
```bash
cd backend
pytest tests/
```

---

## 🌍 Deployment Instructions

LoanTrace is architected as a stateless application with a persistent relational database, making it highly suitable for modern PaaS providers.

**Database (PostgreSQL via Neon/Render/AWS RDS)**:
1. Provision a PostgreSQL 15+ instance.
2. Obtain the connection string.

**Backend (Render / Railway / Heroku)**:
1. Connect your repository to the PaaS.
2. Set Build Command: `pip install -r requirements.txt && alembic upgrade head`
3. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Inject Environment Variables: `DATABASE_URL`, `SECRET_KEY`, `FRONTEND_URL`, `GEMINI_API_KEY`.

**Frontend (Vercel)**:
1. Connect your repository to Vercel.
2. Set Root Directory to `frontend`.
3. Vercel will automatically detect Next.js and apply build settings (`npm run build`).
4. Inject Environment Variable: `NEXT_PUBLIC_API_URL` pointing to your deployed backend URL.

*(Note: Currently, LoanTrace is running locally. No public URL has been configured).*
