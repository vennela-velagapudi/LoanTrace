import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv(os.path.join(os.getcwd(), "backend", ".env"))

from app.services.ai import AIReviewService, AIBatchSummary

ai_service = AIReviewService()
print(f"Is mock? {ai_service.is_mock}")
if ai_service.is_mock:
    print("WARNING: GEMINI_API_KEY is not loaded.")

prompt = "Summarize this batch of exceptions: []"
try:
    res = ai_service._call_gemini(prompt, AIBatchSummary)
    print("Success:", res)
except Exception as e:
    print("Caught Exception:", type(e).__name__, str(e))
