import os
import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Optional

SALT = os.getenv("USER_HASH_SALT", "mediai_secure_salt_2026")


def get_user_hash(user_id: Optional[str]) -> str:
    """
    HIPAA/GDPR Data Privacy Anonymizer (MLOPS_PLAN Section 3):
    Hashes user IDs with a cryptographic salt so real IDs are never written to logs.
    """
    if not user_id:
        return "anonymous"
    return hashlib.sha256(f"{user_id}_{SALT}".encode()).hexdigest()[:12]


class JSONFormatter(logging.Formatter):
    """
    Standard JSON Log Formatter for Cloud Observability (CloudWatch, Datadog, HF Space).
    Serializes records into structured, searchable single-line JSON.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Merge custom telemetry fields attached to LogRecord
        for field in ("request_id", "method", "path", "status_code", "latency_ms", "user_hash"):
            val = getattr(record, field, None)
            if val is not None:
                log_data[field] = val

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str = "mediai") -> logging.Logger:
    """Configure and return the unified MediAI structured logger."""
    app_logger = logging.getLogger(name)
    app_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers on re-import
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        app_logger.addHandler(handler)
        app_logger.propagate = False

    return app_logger


logger = setup_logger("mediai")

