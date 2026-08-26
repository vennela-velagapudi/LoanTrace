import json
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Define structured schemas for AI outputs

class AIExplanation(BaseModel):
    explanation: str = Field(description="Explanation of what failed and why it matters.")
    severity: str = Field(description="AI suggested severity: LOW, MEDIUM, HIGH, or CRITICAL.")
    confidence: str = Field(description="Confidence level: HIGH, MEDIUM, LOW.")

class AISuggestion(BaseModel):
    suggested_value: str = Field(description="The suggested correct value.")
    reason: str = Field(description="Reasoning for the suggestion.")
    confidence: str = Field(description="Confidence level.")

class AIConflictAnalysis(BaseModel):
    analysis: str = Field(description="Analysis of the conflicting values.")
    recommended_value: str = Field(description="The recommended canonical value.")
    reason: str = Field(description="Reasoning for the recommendation.")
    confidence: str = Field(description="Confidence level.")

class AIReviewerNote(BaseModel):
    note: str = Field(description="A concise professional reviewer note.")

class AIBatchSummary(BaseModel):
    total_exceptions_analyzed: int
    severity_distribution: Dict[str, int] = Field(description="Count of each severity level.")
    most_common_rules: List[str] = Field(description="List of the most violated rules.")
    patterns: str = Field(description="Recurring patterns or data quality issues.")
    recommendations: str = Field(description="Recommended review priorities.")

class AIValidationRuleProposal(BaseModel):
    rule_name: str
    description: str
    target_field: str
    operator: str
    threshold: str
    suggested_severity: str
    validation_pseudocode: str
    test_cases: List[str]

class AIReviewService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = "gemini-2.5-flash"
            self.is_mock = False
        else:
            self.client = None
            self.model_name = "demo-mock-model"
            self.is_mock = True

    def _call_gemini(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        if self.is_mock:
            return self._get_mock_response(prompt, schema)
            
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2,
                )
            )
            return schema.model_validate_json(response.text)
        except Exception as e:
            # Fallback to mock on error to prevent crashing the demo
            print(f"Gemini API Error: {e}")
            return self._get_mock_response(prompt, schema)

    def _get_mock_response(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
        # Deterministic mock responses based on schema
        if schema == AIExplanation:
            return schema(
                explanation="[Demo AI] The current value violates the validation rule for this field. This usually indicates a data entry error or missing payment records.",
                severity="HIGH",
                confidence="HIGH"
            )
        elif schema == AISuggestion:
            return schema(
                suggested_value="[Demo AI Suggestion]",
                reason="[Demo AI] Based on historical data patterns and standard bounds.",
                confidence="MEDIUM"
            )
        elif schema == AIConflictAnalysis:
            return schema(
                analysis="[Demo AI] The loan tape and servicer update have conflicting values. The servicer update is typically more recent.",
                recommended_value="[Demo AI Recommendation]",
                reason="[Demo AI] Servicer data is prioritized for active balances.",
                confidence="HIGH"
            )
        elif schema == AIReviewerNote:
            return schema(
                note="[Demo AI] Reviewed discrepancy. The issue appears to stem from a stale loan tape. Suggest confirming with the servicer."
            )
        elif schema == AIBatchSummary:
            return schema(
                total_exceptions_analyzed=100,
                severity_distribution={"CRITICAL": 10, "HIGH": 40, "WARNING": 50},
                most_common_rules=["negative_balance", "missing_document_status"],
                patterns="[Demo AI] Many exceptions relate to missing document statuses and inconsistent payment DPDs.",
                recommendations="[Demo AI] Prioritize resolving CRITICAL negative balance issues first."
            )
        elif schema == AIValidationRuleProposal:
            return schema(
                rule_name="demo_proposed_rule",
                description="[Demo AI] Checks if the value exceeds threshold.",
                target_field="current_balance",
                operator=">",
                threshold="90%",
                suggested_severity="WARNING",
                validation_pseudocode="if current_balance > (0.9 * original_principal): flag()",
                test_cases=["balance=95, principal=100 -> FAIL", "balance=80, principal=100 -> PASS"]
            )
        
        raise ValueError("Unknown schema")

    def explain_exception(self, context: Dict[str, Any]) -> tuple[AIExplanation, str]:
        prompt = f"Explain this loan validation exception to a reviewer:\n{json.dumps(context, indent=2)}\nProvide a clear explanation and assess severity."
        res = self._call_gemini(prompt, AIExplanation)
        return res, prompt

    def suggest_correction(self, context: Dict[str, Any]) -> tuple[AISuggestion, str]:
        prompt = f"Suggest a likely correction for this validation exception:\n{json.dumps(context, indent=2)}\nProvide the exact suggested value and your reasoning."
        res = self._call_gemini(prompt, AISuggestion)
        return res, prompt

    def compare_conflict(self, tape_data: Dict[str, Any], servicer_data: Dict[str, Any], context: Dict[str, Any]) -> tuple[AIConflictAnalysis, str]:
        prompt = f"Compare these conflicting records for an exception:\nTape Data:\n{json.dumps(tape_data, indent=2)}\nServicer Data:\n{json.dumps(servicer_data, indent=2)}\nContext:\n{json.dumps(context, indent=2)}\nRecommend a reliable canonical value."
        res = self._call_gemini(prompt, AIConflictAnalysis)
        return res, prompt

    def generate_note(self, context: Dict[str, Any]) -> tuple[AIReviewerNote, str]:
        prompt = f"Write a concise professional reviewer note summarizing this exception and typical resolution:\n{json.dumps(context, indent=2)}"
        res = self._call_gemini(prompt, AIReviewerNote)
        return res, prompt

    def summarize_batch(self, exceptions_context: List[Dict[str, Any]]) -> tuple[AIBatchSummary, str]:
        limited_context = exceptions_context[:50]
        prompt = f"Summarize this batch of {len(limited_context)} exceptions (showing a sample):\n{json.dumps(limited_context, indent=2)}"
        res = self._call_gemini(prompt, AIBatchSummary)
        return res, prompt

    def generate_rule(self, natural_language: str) -> tuple[AIValidationRuleProposal, str]:
        prompt = f"Generate a structured validation rule proposal from this natural language request:\n\"{natural_language}\""
        res = self._call_gemini(prompt, AIValidationRuleProposal)
        return res, prompt
