"""Workflow state definitions mirroring the original LangGraph implementation."""
from __future__ import annotations

import operator
from datetime import datetime
from typing import Annotated, Dict, List, Optional, TypedDict

from langgraph.graph.message import add_messages


class WorkflowState(TypedDict, total=False):
    """Complete state management for AI Instructions Generation workflow."""

    ocg_term_details: Dict
    document_text: str
    human_labeled_answer: str
    referenced_page_texts: List[str]
    document_name: str
    ocg_term_batch_data: Dict

    initial_ai_instructions: str
    final_ai_instructions: str
    reasoning_explanation: str

    verified_instructions: str
    verification_report: str

    extracted_answer: Annotated[List[str], operator.add]
    extraction_reasoning: Annotated[List[str], operator.add]

    validation_extracted_answer: str
    validation_extraction_reasoning: str

    match_type: str
    judgement: Annotated[List[str], operator.add]
    evaluation_reasoning: str

    validation_match_type: str
    validation_judgement: str
    validation_evaluation_reasoning: str
    validation_is_success: bool
    accuracy_maintained: bool

    refined_instructions: Annotated[List[str], operator.add]
    refinement_reasoning: Annotated[List[str], operator.add]

    is_success: bool
    refinement_attempts: int
    max_refinement_attempts: int
    project_name: str
    workflow_messages: Annotated[List, add_messages]


class WebWorkflowState(WorkflowState, total=False):
    """Extended state for the web application with metadata for monitoring."""

    workflow_id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    progress_percentage: float
    current_stage: str
    can_pause: bool
    can_edit: bool
    intermediate_results: Dict[str, object]
