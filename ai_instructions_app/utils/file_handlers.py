"""Utility helpers for file upload and processing."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple

from ai_instructions_app.config.settings import get_settings


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def validate_file_size(file_bytes: bytes) -> None:
    settings = get_settings()
    if len(file_bytes) > settings.max_file_size:
        raise ValueError("File exceeds maximum allowed size")


def store_file(filename: str, file_bytes: bytes) -> Tuple[Path, str]:
    validate_file_size(file_bytes)
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    destination = UPLOAD_DIR / f"{file_hash}-{filename}"
    destination.write_bytes(file_bytes)
    return destination, file_hash
