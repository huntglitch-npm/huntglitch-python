"""
HuntGlitch HTTP Client
Handles network communication with the HuntGlitch API.
"""

import time
import requests
import logging
from typing import Optional, Dict, Any

from .exceptions import APIError

logger = logging.getLogger(__name__)

HUNTGLITCH_URL = "https://api.huntglitch.com/add-log"


class HuntGlitchClient:
    """
    Handles HTTP communication with HuntGlitch API.
    Manages sessions, retries, and error handling.
    """

    def __init__(
        self,
        timeout: int = 10,
        retries: int = 3,
        retry_delay: float = 1.0,
        silent_failures: bool = True
    ):
        """
        Initialize the client.

        Args:
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            retry_delay: Delay between retries in seconds
            silent_failures: If True, log errors instead of raising
        """
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.silent_failures = silent_failures
        self._session = requests.Session()

    def send(self, payload: Dict[str, Any]) -> bool:
        """
        Send payload to HuntGlitch API.

        Args:
            payload: JSON payload to send

        Returns:
            bool: True if successful, False otherwise
        """
        headers = {"Content-Type": "application/json"}

        for attempt in range(self.retries + 1):
            try:
                response = self._session.post(
                    HUNTGLITCH_URL,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return True

            except requests.exceptions.RequestException as e:
                is_last_attempt = (attempt == self.retries)
                
                if is_last_attempt:
                    error_msg = f"Failed to send log to HuntGlitch after {self.retries + 1} attempts: {e}"
                    if self.silent_failures:
                        logger.error(error_msg)
                        return False
                    else:
                        raise APIError(error_msg) from e
                else:
                    # Retry with delay
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Request failed, retrying in {delay}s... (attempt {attempt + 1}/{self.retries + 1})")
                    time.sleep(delay)

        return False

    def close(self):
        """Close the underlying session."""
        self._session.close()
