"""Workflow management API endpoints."""
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Dict

from flask import Blueprint, jsonify, request

from ai_instructions_app.services.workflow_service import WebWorkflowService
from ai_instructions_app.utils.validation import WorkflowConfigSchema

workflow_bp = Blueprint("workflow", __name__)
workflow_service = WebWorkflowService()


@workflow_bp.post("/")
def start_workflow():
    """Start a new workflow execution."""
    payload: Dict[str, Any] = request.get_json(force=True)
    config = WorkflowConfigSchema(**payload)

    workflow_id = workflow_service.start_workflow(config)
    return jsonify({"workflow_id": workflow_id}), HTTPStatus.ACCEPTED


@workflow_bp.get("/<workflow_id>/status")
def get_status(workflow_id: str):
    """Return the status for a running workflow."""
    status = workflow_service.get_workflow_status(workflow_id)
    if status is None:
        return jsonify({"error": "Workflow not found"}), HTTPStatus.NOT_FOUND
    return jsonify(status)
