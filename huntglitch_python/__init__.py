"""
HuntGlitch Python Logger

A Python package for sending exception logs and custom messages to the HuntGlitch Lighthouse API.
"""

from .logger import HuntGlitchLogger, send_huntglitch_log, capture_exception_and_report

__version__ = "1.0.0"
__author__ = "IT Path Solutions"
__email__ = "support@itpathsolutions.com"

# For backward compatibility
__all__ = [
    "HuntGlitchLogger",
    "send_huntglitch_log",
    "capture_exception_and_report"
]
