# HuntGlitch Python Logger

A Python package for sending exception logs and custom messages to the HuntGlitch. This package provides an easy way to integrate error tracking and logging into your Python applications.

## 📦 Installation

### Option 1: Install from PyPI
```bash
pip install huntglitch-python
```

### Option 2: Install from source
```bash
# Clone the repository
git clone https://github.com/huntglitch-npm/huntglitch-python.git
cd huntglitch-python

# Install the package
pip install .
```

### Option 3: Install from GitHub
```bash
pip install git+https://github.com/huntglitch-npm/huntglitch-python.git
```

## ⚙️ Configuration

The package supports multiple ways to configure your project credentials:

### 1. Environment Variables (Recommended)

Create a `.env` file in your project root:

```env
PROJECT_KEY=your-project-key
DELIVERABLE_KEY=your-deliverable-key
```

Alternative variable names (the library checks both):
```env
HUNTGLITCH_PROJECT_KEY=your-project-key
HUNTGLITCH_DELIVERABLE_KEY=your-deliverable-key
```

### 2. Explicit Configuration

```python
from huntglitch_python import HuntGlitchLogger

logger = HuntGlitchLogger(
    project_key="your-project-key",
    deliverable_key="your-deliverable-key"
)
```

### 3. Environment Variable Locations

The package automatically searches for `.env` files in these locations:
- Current working directory (`./env`)
- Project root (`./env.local`)
- Home directory (`~/.huntglitch.env`)

If you don't have project and deliverable keys, you can get them after creating a new project and deliverable in your HuntGlitch dashboard.

### 4. Production Configuration

For production environments, set environment variables directly:

```bash
export PROJECT_KEY=your-project-key
export DELIVERABLE_KEY=your-deliverable-key
```

Or in Docker:
```dockerfile
ENV PROJECT_KEY=your-project-key
ENV DELIVERABLE_KEY=your-deliverable-key
```

## 🚀 Usage

### Method 1: Class-based API (Recommended for Production)

```python
from huntglitch_python import HuntGlitchLogger

# Initialize with configuration
logger = HuntGlitchLogger(
    project_key="your-project-key",  # Optional if env var is set
    deliverable_key="your-deliverable-key",  # Optional if env var is set
    timeout=10,  # Request timeout
    retries=3,   # Number of retries on failure
    silent_failures=True  # Don't raise on API errors
)

def example_function():
    try:
        # Your code that might raise an exception
        result = 100 / 0
    except Exception:
        # Capture and report the exception
        success = logger.capture_exception(
            additional_data={"user_id": 123, "feature": "calculation"}
        )
        if success:
            print("Error logged successfully")


example_function()
```

### Method 2: Simple Function API (Backward Compatible)

```python
from huntglitch_python import capture_exception_and_report

def example_function():
    try:
        # Your code that might raise an exception
        result = 100 / 0
    except Exception:
        # Capture and report the exception
        capture_exception_and_report()


example_function()
```

### Manual Exception Logging

```python
from huntglitch_python.logger import send_huntglitch_log

try:
    # Your code here
    risky_operation()
except Exception as e:
    send_huntglitch_log(
        error_name=type(e).__name__,
        error_value=str(e),
        file_name=__file__,
        line_number=42,  # Line where error occurred
        log_type=5,  # Error type
        additional_data={"user_id": 123, "action": "risky_operation"}
    )
```

### Using with Additional Data

```python
from huntglitch_python.logger import capture_exception_and_report

def process_user_order(user_id, order_id):
    try:
        # Process order logic
        process_order(order_id)
    except Exception:
        # Report with additional context
        capture_exception_and_report(
            additional_data={
                "user_data": {
                    "user_id": user_id,
                    "name": "John Doe"
                },
                "order_data": {
                    "order_id": order_id,
                    "status": "processing"
                }
            },
            tags={"module": "order_processing", "severity": "high"},
            ip_address="192.168.1.100"
        )
```

### Global Exception Handler

For Flask applications:

```python
from flask import Flask, request
from huntglitch_python.logger import capture_exception_and_report

app = Flask(__name__)

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception to HuntGlitch
    capture_exception_and_report(
        additional_data={"request_url": request.url, "method": request.method}
    )
    # Return error response
    return "Internal Server Error", 500
```

For Django applications (in settings.py):

```python
# Add to your Django settings
import sys
from huntglitch_python.logger import capture_exception_and_report

def custom_exception_handler(exc_type, exc_value, exc_traceback):
    # Log to HuntGlitch
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    capture_exception_and_report()

sys.excepthook = custom_exception_handler
```

## 📋 API Reference

### `send_huntglitch_log()`

Send a custom log entry to HuntGlitch.

**Parameters:**
- `error_name` (str, required): Name of the error/exception
- `error_value` (str, required): Error message or value
- `file_name` (str, required): File where the error occurred
- `line_number` (int, required): Line number where the error occurred
- `error_code` (int, optional): Custom error code (default: 0)
- `log_type` (int, optional): Log type (1=debug, 2=info, 3=notice, 4=warning, 5=error) (default: 5)
- `ip_address` (str, optional): IP address (default: "0.0.0.0")
- `additional_data` (dict, optional): Additional context data
- `tags` (dict, optional): Tags for categorization
- `request_headers` (dict, optional): HTTP request headers
- `request_body` (dict, optional): HTTP request body
- `request_url` (str, optional): Request URL
- `request_method` (str, optional): HTTP method (default: "GET")

### `capture_exception_and_report()`

Automatically capture the current exception and report it to HuntGlitch.

**Parameters:**
- `**kwargs`: Any additional parameters supported by `send_huntglitch_log()`

## 🔧 Log Types

| Type | Value | Description |
|------|-------|-------------|
| Debug | 1 | Debug information |
| Info | 2 | Informational messages |
| Notice | 3 | Normal but significant conditions |
| Warning | 4 | Warning conditions |
| Error | 5 | Error conditions (default) |

You can use either string or integer values:

```python
logger.send_log(..., log_type="warning")  # String
logger.send_log(..., log_type=4)          # Integer
```

## 🛡️ Production-Ready Features

### Retry Logic with Exponential Backoff
The logger automatically retries failed requests with exponential backoff:

```python
logger = HuntGlitchLogger(
    retries=3,           # Number of retry attempts
    retry_delay=1.0,     # Base delay between retries
    timeout=10           # Request timeout
)
```

### Silent Failure Mode
In production, you may want to continue execution even if logging fails:

```python
logger = HuntGlitchLogger(
    silent_failures=True  # Log errors instead of raising exceptions
)

# Returns True/False instead of raising exceptions
success = logger.capture_exception()
```

### Configuration Validation
The package validates configuration on initialization:

```python
try:
    logger = HuntGlitchLogger()  # Will raise ConfigurationError if keys missing
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Error Handling
Custom exceptions for different error types:

```python
from huntglitch_python import ConfigurationError, APIError, HuntGlitchError

try:
    logger = HuntGlitchLogger(silent_failures=False)
    logger.send_log(...)
except ConfigurationError:
    print("Missing or invalid configuration")
except APIError:
    print("API request failed")
except HuntGlitchError:
    print("Other HuntGlitch error")
```

## 🌐 Framework Integration Examples

### FastAPI

```python
from fastapi import FastAPI, HTTPException, Request
from huntglitch_python.logger import capture_exception_and_report

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    capture_exception_and_report(
        additional_data={
            "request_url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers)
        }
    )
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Celery Tasks

```python
from celery import Celery
from huntglitch_python.logger import capture_exception_and_report

app = Celery('tasks')

@app.task(bind=True)
def process_data(self, data):
    try:
        # Process data
        return process_complex_data(data)
    except Exception:
        capture_exception_and_report(
            additional_data={
                "task_id": self.request.id,
                "task_name": "process_data",
                "input_data": data
            }
        )
        raise
```

### Asyncio Applications

```python
import asyncio
from huntglitch_python.logger import capture_exception_and_report

async def async_process():
    try:
        # Async operations
        await some_async_operation()
    except Exception:
        capture_exception_and_report(
            additional_data={"operation": "async_process"}
        )
        raise

# For global async exception handling
def handle_exception(loop, context):
    exception = context.get('exception')
    if exception:
        capture_exception_and_report(
            additional_data={"context": str(context)}
        )

loop = asyncio.get_event_loop()
loop.set_exception_handler(handle_exception)
```

## 🔄 Alternative Usage Methods

### As a Decorator

You can create a decorator for automatic error reporting:

```python
import functools
from huntglitch_python.logger import capture_exception_and_report

def log_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            capture_exception_and_report(
                additional_data={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            raise
    return wrapper

# Usage
@log_exceptions
def risky_function():
    # Your code here
    pass
```

### Context Manager

```python
from contextlib import contextmanager
from huntglitch_python.logger import capture_exception_and_report

@contextmanager
def error_reporting(operation_name):
    try:
        yield
    except Exception:
        capture_exception_and_report(
            additional_data={"operation": operation_name}
        )
        raise

# Usage
with error_reporting("database_operation"):
    # Your database code here
    pass
```

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

### Project Structure

```
huntglitch-python/
├── huntglitch_python/
│   ├── __init__.py
│   └── logger.py
├── tests/
│   └── test_logger.py
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README.md
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔍 Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Ensure `PROJECT_KEY` and `DELIVERABLE_KEY` are set
2. **Network Issues**: Check if the API endpoint is accessible
3. **Import Errors**: Verify the package is properly installed

### Debug Mode

For debugging, you can catch and print any errors from the logging itself:

```python
from huntglitch_python.logger import send_huntglitch_log

try:
    # Your code
    pass
except Exception as e:
    try:
        send_huntglitch_log(
            error_name=type(e).__name__,
            error_value=str(e),
            file_name=__file__,
            line_number=10
        )
    except Exception as log_error:
        print(f"Failed to log to HuntGlitch: {log_error}")
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, email support@huntglitch.com or create an issue in this repository.
