"""Health check endpoints for the AI Instructions Generator service."""
from __future__ import annotations

from flask import Blueprint, jsonify


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    """Return a simple health status payload."""
    return jsonify({"status": "ok"})
