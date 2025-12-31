"""
HuntGlitch Exceptions
"""

class HuntGlitchError(Exception):
    """Base exception for HuntGlitch errors."""
    pass


class ConfigurationError(HuntGlitchError):
    """Raised when configuration is invalid."""
    pass


class APIError(HuntGlitchError):
    """Raised when API request fails."""
    pass
