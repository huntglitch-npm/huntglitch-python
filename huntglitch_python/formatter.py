"""
HuntGlitch Log Formatter
Handles data transformation for HuntGlitch API.
"""

import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Union

# Log types mapping
LOG_TYPES = {
    'debug': 1,
    'info': 2,
    'notice': 3,
    'warning': 4,
    'error': 5
}

class LogFormatter:
    """
    Formats log data into the specific JSON structure required by HuntGlitch.
    """

    def prepare_error_data(
        self,
        error_name: str,
        error_value: str,
        file_name: str,
        line_number: int,
        error_code: int = 0
    ) -> Dict[str, Any]:
        """Prepare error data structure."""
        return {
            "c": str(error_value)[:1000],  # Limit error message length
            "d": str(file_name),
            "e": [],
            "f": int(line_number),
            "g": error_code,
            "h": str(error_name),
        }

    def prepare_log_data(
        self,
        error_data: Dict[str, Any],
        additional_data: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
        request_method: str = "GET"
    ) -> Dict[str, Any]:
        """Prepare log data structure."""
        return {
            "b": error_data,
            "i": additional_data or {},
            "j": tags or {},
            "k": request_headers or {},
            "l": request_body or {},
            "m": request_url or "",
            "n": request_method,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def prepare_payload(
        self,
        project_key: str,
        deliverable_key: str,
        log_data: Dict[str, Any],
        log_type: Union[int, str],
        ip_address: str = "0.0.0.0"
    ) -> Dict[str, Any]:
        """Prepare API payload."""
        # Convert string log type to int
        if isinstance(log_type, str):
            log_type = LOG_TYPES.get(log_type.lower(), 5)

        return {
            "vp": project_key,
            "vd": deliverable_key,
            "o": log_type,
            "a": json.dumps(log_data, default=str),  # Handle datetime serialization
            "r": ip_address,
        }
