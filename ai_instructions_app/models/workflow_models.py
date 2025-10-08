"""Database models representing workflows and related artifacts."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ai_instructions_app.models.database import db


class WorkflowStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Workflow(db.Model):
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    status = Column(SAEnum(WorkflowStatus), default=WorkflowStatus.pending)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="workflow")
    instructions = relationship("Instruction", back_populates="workflow")


class Document(db.Model):
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey("workflow.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("Workflow", back_populates="documents")


class Instruction(db.Model):
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey("workflow.id"))
    version = Column(Integer, default=1)
    content = Column(Text, nullable=False)
    evaluation_score = Column(Float, nullable=True)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    workflow = relationship("Workflow", back_populates="instructions")
    evaluations = relationship("EvaluationResult", back_populates="instruction")


class EvaluationResult(db.Model):
    id = Column(String, primary_key=True)
    instruction_id = Column(String, ForeignKey("instruction.id"))
    match_type = Column(String, nullable=False)
    extracted_answer = Column(Text, nullable=False)
    human_answer = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)

    instruction = relationship("Instruction", back_populates="evaluations")
