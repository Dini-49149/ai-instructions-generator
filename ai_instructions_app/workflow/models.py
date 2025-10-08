"""Structured output models for the LangGraph workflow."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AIInstructionsOutput(BaseModel):
    initial_ai_instructions: str
    reasoning_explanation: str


class VerificationOutput(BaseModel):
    verified_instructions: str
    verification_report: str


class ExtractionOutput(BaseModel):
    extracted_answer: str
    extraction_reasoning: str


class EvaluationOutput(BaseModel):
    judgment: Literal["YES", "NO", "PARTIAL"]
    reasoning: str


class RefinementOutput(BaseModel):
    refined_instructions: str
    refinement_reasoning: str
