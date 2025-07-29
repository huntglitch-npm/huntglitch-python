"""
HuntGlitch Python Logger - Usage Examples

This file demonstrates various ways to use the HuntGlitch Python logger
in different scenarios and frameworks.
"""

import os
from huntglitch_python import HuntGlitchLogger, send_huntglitch_log, capture_exception_and_report

# Example 1: Basic usage with environment variables
def basic_usage_example():
    """
    Basic usage assuming environment variables are set.
    Requires PROJECT_KEY and DELIVERABLE_KEY in environment.
    """
    try:
        # This will cause a division by zero error
        result = 10 / 0
    except Exception:
        # Simple exception capture and report
        capture_exception_and_report()
        print("Exception reported to HuntGlitch")


# Example 2: Using HuntGlitchLogger class with explicit configuration
def explicit_config_example():
    """
    Using the logger class with explicit configuration.
    Good for when you want to avoid environment variables.
    """
    logger = HuntGlitchLogger(
        project_key="your-project-key",
        deliverable_key="your-deliverable-key",
        timeout=15,  # Custom timeout
        retries=2,   # Custom retry count
        silent_failures=True  # Don't raise exceptions on API failures
    )
    
    try:
        # Simulate an error
        raise ValueError("This is a test error")
    except Exception:
        success = logger.capture_exception(
            additional_data={
                "user_id": 12345,
                "feature": "payment_processing"
            },
            tags={"environment": "production", "severity": "high"}
        )
        
        if success:
            print("Exception logged successfully")
        else:
            print("Failed to log exception")


# Example 3: Manual logging without exceptions
def manual_logging_example():
    """
    Manually logging events without actual exceptions.
    Useful for custom events and debugging.
    """
    logger = HuntGlitchLogger(
        project_key=os.getenv("PROJECT_KEY"),
        deliverable_key=os.getenv("DELIVERABLE_KEY")
    )
    
    # Log a custom event
    logger.send_log(
        error_name="CustomEvent",
        error_value="User login attempt failed",
        file_name=__file__,
        line_number=60,
        log_type="warning",  # Can use string or int
        additional_data={
            "username": "john_doe",
            "ip_address": "192.168.1.100",
            "attempt_count": 3
        }
    )


# Example 4: Decorator for automatic error logging
def error_logging_decorator(func):
    """
    Decorator that automatically logs exceptions from functions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the exception
            capture_exception_and_report(
                additional_data={
                    "function_name": func.__name__,
                    "args": str(args)[:500],  # Limit size
                    "kwargs": str(kwargs)[:500]
                }
            )
            # Re-raise the exception
            raise
    return wrapper


@error_logging_decorator
def risky_function(data):
    """Example function that might fail."""
    if not data:
        raise ValueError("Data cannot be empty")
    return data.upper()


# Example 5: Flask application integration
def flask_integration_example():
    """
    Example of integrating with Flask application.
    """
    try:
        from flask import Flask, request
    except ImportError:
        print("Flask not installed - skipping Flask example")
        return
    
    app = Flask(__name__)
    
    # Initialize logger
    logger = HuntGlitchLogger(
        project_key=os.getenv("PROJECT_KEY"),
        deliverable_key=os.getenv("DELIVERABLE_KEY")
    )
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler for Flask."""
        logger.capture_exception(
            additional_data={
                "request_url": request.url,
                "request_method": request.method,
                "user_agent": request.headers.get('User-Agent'),
                "remote_addr": request.remote_addr
            }
        )
        return "Internal Server Error", 500
    
    @app.route("/test-error")
    def test_error():
        """Route that intentionally causes an error."""
        raise RuntimeError("This is a test error")
    
    return app


# Example 6: Context manager for error logging
class ErrorLoggingContext:
    """Context manager for automatic error logging."""
    
    def __init__(self, operation_name, **extra_data):
        self.operation_name = operation_name
        self.extra_data = extra_data
        self.logger = HuntGlitchLogger(
            project_key=os.getenv("PROJECT_KEY"),
            deliverable_key=os.getenv("DELIVERABLE_KEY")
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.capture_exception(
                additional_data={
                    "operation": self.operation_name,
                    **self.extra_data
                }
            )
        return False  # Don't suppress the exception


def context_manager_example():
    """Example using context manager for error logging."""
    with ErrorLoggingContext("database_operation", table="users", action="insert"):
        # Simulate database operation
        raise RuntimeError("Database connection failed")


# Example 7: Async/await support
async def async_example():
    """
    Example with async/await.
    The logger itself is not async, but can be used in async contexts.
    """
    import asyncio
    
    logger = HuntGlitchLogger(
        project_key=os.getenv("PROJECT_KEY"),
        deliverable_key=os.getenv("DELIVERABLE_KEY")
    )
    
    try:
        # Simulate async operation
        await asyncio.sleep(1)
        raise RuntimeError("Async operation failed")
    except Exception:
        # Note: This is a synchronous call within async function
        # For truly async logging, you'd need to wrap in asyncio.create_task
        logger.capture_exception(
            additional_data={"operation_type": "async"}
        )


# Example 8: Configuration validation
def configuration_example():
    """
    Example showing configuration validation and error handling.
    """
    try:
        # This will raise ConfigurationError if env vars are not set
        logger = HuntGlitchLogger()
        print("Logger configured successfully")
    except Exception as e:
        print(f"Configuration error: {e}")
        print("Please set PROJECT_KEY and DELIVERABLE_KEY environment variables")
        
        # Alternative: provide config explicitly
        logger = HuntGlitchLogger(
            project_key="your-project-key",
            deliverable_key="your-deliverable-key",
            silent_failures=True  # Don't raise on API errors
        )
        print("Logger configured with explicit keys")


if __name__ == "__main__":
    """
    Run examples (make sure to set environment variables first).
    """
    print("HuntGlitch Logger Examples")
    print("=" * 40)
    
    # Check if configuration is available
    if not (os.getenv("PROJECT_KEY") and os.getenv("DELIVERABLE_KEY")):
        print("Warning: PROJECT_KEY and DELIVERABLE_KEY not set in environment")
        print("Some examples may not work correctly")
    
    # Run examples
    print("\n1. Configuration example:")
    configuration_example()
    
    print("\n2. Manual logging example:")
    try:
        manual_logging_example()
        print("Manual log sent successfully")
    except Exception as e:
        print(f"Manual logging failed: {e}")
    
    print("\n3. Decorator example:")
    try:
        risky_function("")  # This will cause an error
    except ValueError as e:
        print(f"Function failed as expected: {e}")
    
    print("\n4. Context manager example:")
    try:
        context_manager_example()
    except RuntimeError as e:
        print(f"Context manager caught error: {e}")
    
    print("\nExamples completed!")
