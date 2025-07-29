"""
Tests for HuntGlitch Python Logger
"""

import os
import pytest
from unittest.mock import Mock, patch

from huntglitch_python.logger import (
    HuntGlitchLogger,
    send_huntglitch_log,
    capture_exception_and_report,
    ConfigurationError,
    APIError,
    LOG_TYPES
)


class TestHuntGlitchLogger:
    """Test cases for HuntGlitchLogger class."""

    def setup_method(self):
        """Setup for each test method."""
        self.project_key = "test-project-key"
        self.deliverable_key = "test-deliverable-key"

    def test_initialization_with_params(self):
        """Test logger initialization with parameters."""
        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            load_env=False
        )
        assert logger.project_key == self.project_key
        assert logger.deliverable_key == self.deliverable_key

    def test_initialization_missing_config(self):
        """Test that missing configuration raises error."""
        with pytest.raises(ConfigurationError):
            HuntGlitchLogger(load_env=False)

    @patch.dict(os.environ, {'PROJECT_KEY': 'env-project', 'DELIVERABLE_KEY': 'env-deliverable'})
    def test_initialization_from_env(self):
        """Test initialization from environment variables."""
        logger = HuntGlitchLogger(load_env=False)
        assert logger.project_key == 'env-project'
        assert logger.deliverable_key == 'env-deliverable'

    def test_log_types_conversion(self):
        """Test log type string to int conversion."""
        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            load_env=False
        )

        # Test string log types
        for log_type_str, expected_int in LOG_TYPES.items():
            payload = logger._prepare_payload({}, log_type_str)
            assert payload['o'] == expected_int

    @patch('huntglitch_python.logger.requests.post')
    def test_successful_log_send(self, mock_post):
        """Test successful log sending."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            load_env=False
        )

        result = logger.send_log(
            error_name="TestError",
            error_value="Test error message",
            file_name="test.py",
            line_number=42
        )

        assert result is True
        assert mock_post.called

    @patch('huntglitch_python.logger.requests.post')
    def test_retry_logic(self, mock_post):
        """Test retry logic on failed requests."""
        # Mock first call to fail, second to succeed
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = Exception("Network error")

        mock_response_success = Mock()
        mock_response_success.raise_for_status.return_value = None

        mock_post.side_effect = [
            mock_response_fail,
            mock_response_success
        ]

        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            retries=1,
            retry_delay=0.01,  # Fast retry for testing
            load_env=False
        )

        result = logger.send_log(
            error_name="TestError",
            error_value="Test error message",
            file_name="test.py",
            line_number=42
        )

        assert result is True
        assert mock_post.call_count == 2

    @patch('huntglitch_python.logger.requests.post')
    def test_silent_failure_mode(self, mock_post):
        """Test silent failure mode."""
        mock_post.side_effect = Exception("Network error")

        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            retries=0,
            silent_failures=True,
            load_env=False
        )

        result = logger.send_log(
            error_name="TestError",
            error_value="Test error message",
            file_name="test.py",
            line_number=42
        )

        assert result is False  # Should return False instead of raising

    @patch('huntglitch_python.logger.requests.post')
    def test_non_silent_failure_mode(self, mock_post):
        """Test non-silent failure mode."""
        mock_post.side_effect = Exception("Network error")

        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            retries=0,
            silent_failures=False,
            load_env=False
        )

        with pytest.raises(APIError):
            logger.send_log(
                error_name="TestError",
                error_value="Test error message",
                file_name="test.py",
                line_number=42
            )

    def test_capture_exception_no_active_exception(self):
        """Test capturing exception when none is active."""
        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            silent_failures=True,
            load_env=False
        )

        result = logger.capture_exception()
        assert result is False

    @patch('huntglitch_python.logger.requests.post')
    def test_capture_exception_with_active_exception(self, mock_post):
        """Test capturing active exception."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        logger = HuntGlitchLogger(
            project_key=self.project_key,
            deliverable_key=self.deliverable_key,
            load_env=False
        )

        try:
            raise ValueError("Test exception")
        except ValueError:
            result = logger.capture_exception(
                additional_data={"test": "data"}
            )
            assert result is True


class TestBackwardCompatibility:
    """Test backward compatibility functions."""

    @patch.dict(os.environ, {'PROJECT_KEY': 'test-project', 'DELIVERABLE_KEY': 'test-deliverable'})
    @patch('huntglitch_python.logger.requests.post')
    def test_send_huntglitch_log_function(self, mock_post):
        """Test the backward compatibility function."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = send_huntglitch_log(
            error_name="TestError",
            error_value="Test error message",
            file_name="test.py",
            line_number=42
        )

        assert result is True
        assert mock_post.called

    @patch.dict(os.environ, {'PROJECT_KEY': 'test-project', 'DELIVERABLE_KEY': 'test-deliverable'})
    @patch('huntglitch_python.logger.requests.post')
    def test_capture_exception_and_report_function(self, mock_post):
        """Test the backward compatibility exception capture function."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        try:
            raise RuntimeError("Test exception")
        except RuntimeError:
            result = capture_exception_and_report()
            assert result is True
            assert mock_post.called


if __name__ == "__main__":
    pytest.main([__file__])
