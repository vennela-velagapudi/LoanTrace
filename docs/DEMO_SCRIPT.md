# LoanTrace — Official Demo Script

This script outlines the end-to-end journey to successfully demonstrate the full capabilities of the LoanTrace platform.

## Prerequisites
1. Ensure the backend and frontend are running (`uvicorn app.main:app` and `npm run dev`).
2. Run `python scripts/generate_synthetic_data.py` to ensure the `data/` folder is populated with the deterministic mock dataset.

---

## 🎬 Act 1: Ingestion & Validation (The Data Operator)
1. Navigate to `http://localhost:3000/login`.
2. Click **operator** in the Demo Credentials section to auto-fill the form, then click **Sign In**.
3. You will be routed to the **Data Operator Dashboard**.
4. In the Upload Data widget, upload `data/loan_tape.csv`. Wait for the success alert.
5. Upload `data/servicer_update.csv`. Wait for the success alert.
6. Upload `data/document_manifest.csv`. Wait for the success alert.
7. Click the **Run Cross-Source Validation** button. The deterministic rules engine will analyze the merged schema and generate anomalies.
8. Point out the dashboard metrics (e.g., Total Loans, Open Exceptions, Data Quality Score).
9. **Log out**.

---

## 🎬 Act 2: Human-AI Collaboration (The Reviewer)
1. Log in as **reviewer**.
2. You are routed to the **Reviewer Exception Queue**. Notice the list of anomalies categorized by severity (CRITICAL, HIGH, WARNING).
3. Click on an exception (e.g., a `negative_balance` or `cross_source_conflict`).
4. **The Split-Screen Workspace**:
   * **Left Panel**: Displays the immutable raw lineage alongside editable canonical fields.
   * **Right Panel**: Houses the AI Review Assistant and Audit Timeline.
5. **Demonstrate AI Capabilities**:
   * Click **Explain Issue**. The AI will parse the exact field boundaries and generate a readable analysis.
   * Click **Suggest Correction**. The AI will mathematically or logically infer the correct value.
   * If it's a conflict, click **Compare Sources** for a side-by-side logical deduction.
   * Click **Generate Note** to auto-fill the reviewer decision reasoning.
6. **Human-in-the-Loop**:
   * Click **[Accept & Edit]** on the AI's suggestion. Note that this *only* populates the human's input form—it does *not* silently mutate the database.
   * Click **Approve Exception**. The backend will automatically re-run validation constraints on this loan.
7. Click the **Finalize & Verify Loan Record** button (which appears only if all exceptions for that loan are resolved). A success notification will appear.
8. Navigate to **AI Tools** from the sidebar to demonstrate **Batch Summarization** and **Natural Language Rule Generation**.
9. **Log out**.

---

## 🎬 Act 3: Immutability & Traceability (The Data Consumer)
1. Log in as **consumer**.
2. You are routed to the **Verified Data Consumer** dashboard.
3. Observe the **Data Quality Score** and the read-only **Verified Ledger**.
4. Click on the Verified Record ID generated in Act 2.
5. Point out the cryptographic **SHA-256 Checksum** proving the record's canonical data integrity.
6. Scroll through the **Verification Lineage**, tracing the record back to its raw batch upload.
7. Review the **Complete Audit Trail**, noting how System, AI, and Human actions are permanently intertwined.
8. Return to the dashboard and click **Export Verified CSV** to download the clean, downstream dataset.

**Demo Concluded.**
