import os
import json
import requests
import sys
import traceback
import logging
import time
from typing import Optional, Dict, Any, Union
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Constants
DEFAULT_TIMEOUT = 10
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
HUNTGLITCH_URL = "https://api.huntglitch.com/add-log"

# Log types mapping
LOG_TYPES = {
    'debug': 1,
    'info': 2, 
    'notice': 3,
    'warning': 4,
    'error': 5
}

# Setup internal logger
logger = logging.getLogger(__name__)


class HuntGlitchError(Exception):
    """Base exception for HuntGlitch errors."""
    pass


class ConfigurationError(HuntGlitchError):
    """Raised when configuration is invalid."""
    pass


class APIError(HuntGlitchError):
    """Raised when API request fails."""
    pass


class HuntGlitchLogger:
    """
    Production-ready HuntGlitch logger with configuration management,
    error handling, and retry logic.
    """
    
    def __init__(
        self,
        project_key: Optional[str] = None,
        deliverable_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
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
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.silent_failures = silent_failures
        
        # Load environment variables if requested and available
        if load_env and DOTENV_AVAILABLE:
            self._load_env_files()
        
        # Set configuration
        self.project_key = project_key or os.getenv("PROJECT_KEY") or os.getenv("HUNTGLITCH_PROJECT_KEY")
        self.deliverable_key = deliverable_key or os.getenv("DELIVERABLE_KEY") or os.getenv("HUNTGLITCH_DELIVERABLE_KEY")
        
        # Validate configuration
        self._validate_config()
    
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
    
    def _prepare_error_data(
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
    
    def _prepare_log_data(
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
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def _prepare_payload(
        self,
        log_data: Dict[str, Any],
        log_type: Union[int, str],
        ip_address: str = "0.0.0.0"
    ) -> Dict[str, Any]:
        """Prepare API payload."""
        # Convert string log type to int
        if isinstance(log_type, str):
            log_type = LOG_TYPES.get(log_type.lower(), 5)
        
        return {
            "vp": self.project_key,
            "vd": self.deliverable_key,
            "o": log_type,
            "a": json.dumps(log_data, default=str),  # Handle datetime serialization
            "r": ip_address,
        }
    
    def _make_request(self, payload: Dict[str, Any]) -> Optional[requests.Response]:
        """Make HTTP request with retry logic."""
        headers = {"Content-Type": "application/json"}
        
        for attempt in range(self.retries + 1):
            try:
                response = requests.post(
                    HUNTGLITCH_URL,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == self.retries:
                    # Last attempt failed
                    error_msg = f"Failed to send log to HuntGlitch after {self.retries + 1} attempts: {e}"
                    if self.silent_failures:
                        logger.error(error_msg)
                        return None
                    else:
                        raise APIError(error_msg) from e
                else:
                    # Retry with delay
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    logger.warning(f"Request failed, retrying... (attempt {attempt + 1}/{self.retries + 1})")
        
        return None
    
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
            error_data = self._prepare_error_data(
                error_name, error_value, file_name, line_number, error_code
            )
            
            log_data = self._prepare_log_data(
                error_data, additional_data, tags, request_headers,
                request_body, request_url, request_method
            )
            
            payload = self._prepare_payload(log_data, log_type, ip_address)
            
            response = self._make_request(payload)
            return response is not None
            
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
