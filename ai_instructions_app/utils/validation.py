"""Input validation helpers using Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowConfigSchema(BaseModel):
    """Schema describing the required configuration to start a workflow."""

    ocg_term_details: Dict[str, Any]
    data_definitions: Dict[str, Any] = Field(default_factory=dict)
    document_text: str
    human_labeled_answer: str
    referenced_page_texts: List[str]
    document_name: str
    project_name: str

    class Config:
        extra = "forbid"


class WorkflowStatusPayload(BaseModel):
    """Schema representing the workflow status payload returned by the API."""

    workflow_id: str
    status: str
    progress: float
    current_stage: str
    created_at: datetime
    updated_at: datetime
    result: Optional[Dict[str, Any]] = None
