"""
HuntGlitch Python Logger

A Python package for sending exception logs and custom messages to the HuntGlitch.
"""

from .logger import HuntGlitchLogger, send_huntglitch_log, capture_exception_and_report

__version__ = "1.2.0"
__author__ = "HuntGlitch"
__email__ = "support@huntglitch.com"

# For backward compatibility
__all__ = [
    "HuntGlitchLogger",
    "send_huntglitch_log",
    "capture_exception_and_report"
]
