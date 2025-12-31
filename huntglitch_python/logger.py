import os
import sys
import traceback
import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from .exceptions import HuntGlitchError, ConfigurationError, APIError
from .client import HuntGlitchClient
from .formatter import LogFormatter, LOG_TYPES

# Setup internal logger
logger = logging.getLogger(__name__)


# Re-export exceptions for backward compatibility
__all__ = [
    'HuntGlitchLogger', 
    'send_huntglitch_log', 
    'capture_exception_and_report',
    'HuntGlitchError', 
    'ConfigurationError', 
    'APIError',
    'LOG_TYPES'
]


class HuntGlitchLogger:
    """
    Production-ready HuntGlitch logger with configuration management,
    error handling, and retry logic.
    """

    def __init__(
        self,
        project_key: Optional[str] = None,
        deliverable_key: Optional[str] = None,
        timeout: int = 10,
        retries: int = 3,
        retry_delay: float = 1.0,
        silent_failures: bool = True,
        load_env: bool = True
    ):
        """
        Initialize HuntGlitch logger.

        Args:
            project_key: Project key (overrides env var)
            deliverable_key: Deliverable key (overrides env var)
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            retry_delay: Delay between retries in seconds
            silent_failures: If True, log errors instead of raising
            load_env: Whether to load environment variables
        """
        self.silent_failures = silent_failures

        # Load environment variables if requested and available
        if load_env and DOTENV_AVAILABLE:
            self._load_env_files()

        # Set configuration
        self.project_key = project_key or os.getenv("PROJECT_KEY") or os.getenv("HUNTGLITCH_PROJECT_KEY")
        self.deliverable_key = deliverable_key or os.getenv("DELIVERABLE_KEY") or os.getenv("HUNTGLITCH_DELIVERABLE_KEY")

        # Validate configuration
        self._validate_config()

        # Initialize components
        self.client = HuntGlitchClient(
            timeout=timeout,
            retries=retries,
            retry_delay=retry_delay,
            silent_failures=silent_failures
        )
        self.formatter = LogFormatter()

    def _load_env_files(self):
        """Load environment variables from various .env file locations."""
        env_files = [
            '.env',
            '.env.local',
            Path.cwd() / '.env',
            Path.cwd() / '.env.local',
            Path.home() / '.huntglitch.env'
        ]

        for env_file in env_files:
            if isinstance(env_file, str):
                env_file = Path(env_file)
            if env_file.exists():
                load_dotenv(env_file)
                logger.debug(f"Loaded environment from {env_file}")
                break

    def _validate_config(self):
        """Validate configuration."""
        if not self.project_key:
            raise ConfigurationError(
                "PROJECT_KEY is required. Set it via environment variable or constructor parameter."
            )
        if not self.deliverable_key:
            raise ConfigurationError(
                "DELIVERABLE_KEY is required. Set it via environment variable or constructor parameter."
            )

    # Kept for backward compatibility if anyone was using it, though it was private
    def _prepare_payload(self, *args, **kwargs):
        """Deprecated: Internal method moved to LogFormatter."""
        return self.formatter.prepare_payload(self.project_key, self.deliverable_key, *args, **kwargs)

    def send_log(
        self,
        error_name: str,
        error_value: str,
        file_name: str,
        line_number: int,
        *,
        error_code: int = 0,
        log_type: Union[int, str] = 5,
        ip_address: str = "0.0.0.0",
        additional_data: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        request_url: Optional[str] = None,
        request_method: str = "GET"
    ) -> bool:
        """
        Send a log entry to HuntGlitch.

        Returns:
            bool: True if successful, False if failed (when silent_failures=True)
        """
        try:
            error_data = self.formatter.prepare_error_data(
                error_name, error_value, file_name, line_number, error_code
            )

            log_data = self.formatter.prepare_log_data(
                error_data, additional_data, tags, request_headers,
                request_body, request_url, request_method
            )

            payload = self.formatter.prepare_payload(
                self.project_key, self.deliverable_key, log_data, log_type, ip_address
            )

            return self.client.send(payload)

        except HuntGlitchError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error in send_log: {e}"
            if self.silent_failures:
                logger.error(error_msg)
                return False
            else:
                raise HuntGlitchError(error_msg) from e

    def capture_exception(self, **kwargs) -> bool:
        """
        Capture current exception and send to HuntGlitch.

        Returns:
            bool: True if successful, False if failed
        """
        exc_type, exc_value, exc_traceback = sys.exc_info()

        if exc_type is None:
            if not self.silent_failures:
                raise HuntGlitchError("No active exception to capture")
            logger.warning("No active exception to capture")
            return False

        try:
            # Get the last frame from traceback
            tb_frame = traceback.extract_tb(exc_traceback)[-1]
            file_name = tb_frame.filename
            line_number = tb_frame.lineno

            return self.send_log(
                error_name=exc_type.__name__,
                error_value=str(exc_value),
                file_name=file_name,
                line_number=line_number,
                **kwargs
            )
        except Exception as e:
            error_msg = f"Failed to capture exception: {e}"
            if self.silent_failures:
                logger.error(error_msg)
                return False
            else:
                raise HuntGlitchError(error_msg) from e


# Global logger instance for backward compatibility
_default_logger = None


def _get_default_logger() -> HuntGlitchLogger:
    """Get or create default logger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = HuntGlitchLogger()
    return _default_logger


def send_huntglitch_log(
    error_name: str,
    error_value: str,
    file_name: str,
    line_number: int,
    *,
    error_code: int = 0,
    log_type: Union[int, str] = 5,
    ip_address: str = "0.0.0.0",
    additional_data: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, Any]] = None,
    request_headers: Optional[Dict[str, Any]] = None,
    request_body: Optional[Dict[str, Any]] = None,
    request_url: Optional[str] = None,
    request_method: str = "GET"
) -> bool:
    """
    Send a log entry to HuntGlitch using the default logger.

    This function maintains backward compatibility with the original API.
    """
    logger_instance = _get_default_logger()
    return logger_instance.send_log(
        error_name=error_name,
        error_value=error_value,
        file_name=file_name,
        line_number=line_number,
        error_code=error_code,
        log_type=log_type,
        ip_address=ip_address,
        additional_data=additional_data,
        tags=tags,
        request_headers=request_headers,
        request_body=request_body,
        request_url=request_url,
        request_method=request_method
    )


def capture_exception_and_report(**kwargs) -> bool:
    """
    Capture current exception and report using the default logger.

    This function maintains backward compatibility with the original API.
    """
    logger_instance = _get_default_logger()
    return logger_instance.capture_exception(**kwargs)
