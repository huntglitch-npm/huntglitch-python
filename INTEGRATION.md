# Integration Guide for HuntGlitch Python Logger

This guide shows how to integrate the HuntGlitch Python logger into different types of Python projects.

## For New Projects

1. **Install the package:**
   ```bash
   pip install huntglitch-python
   # or with dotenv support
   pip install huntglitch-python[env]
   ```

2. **Copy the configuration template:**
   ```bash
   cp env.example .env
   ```

3. **Edit `.env` with your credentials:**
   ```env
   PROJECT_KEY=your-actual-project-key
   DELIVERABLE_KEY=your-actual-deliverable-key
   ```

4. **Add to your main application file:**
   ```python
   from huntglitch_python import HuntGlitchLogger
   
   # Initialize logger once at application startup
   logger = HuntGlitchLogger()
   
   # Use throughout your application
   try:
       # Your application code
       pass
   except Exception:
       logger.capture_exception()
   ```

## For Existing Projects

### Step 1: Install and Configure
```bash
pip install huntglitch-python[env]
```

Add to your existing `.env` file or create one:
```env
PROJECT_KEY=your-project-key
DELIVERABLE_KEY=your-deliverable-key
```

### Step 2: Initialize in Your Main Module
```python
# main.py or __init__.py
from huntglitch_python import HuntGlitchLogger

# Create a global logger instance
error_logger = HuntGlitchLogger(
    silent_failures=True,  # Don't crash app on logging failures
    retries=2,            # Retry failed requests
    timeout=5             # 5-second timeout
)

# Export for use in other modules
__all__ = ['error_logger']
```

### Step 3: Use in Other Modules
```python
# any_module.py
from main import error_logger

def some_function():
    try:
        # Your existing code
        risky_operation()
    except Exception:
        # Add this single line to existing exception handlers
        error_logger.capture_exception(
            additional_data={"module": __name__, "function": "some_function"}
        )
        # Your existing error handling continues here
        raise  # or handle as you normally would
```

## Framework-Specific Integration

### Django Projects

1. **Add to settings.py:**
   ```python
   # settings.py
   from huntglitch_python import HuntGlitchLogger
   
   HUNTGLITCH_LOGGER = HuntGlitchLogger(
       project_key=env('PROJECT_KEY'),
       deliverable_key=env('DELIVERABLE_KEY'),
       silent_failures=True
   )
   ```

2. **Create a middleware (optional):**
   ```python
   # middleware.py
   from django.conf import settings
   
   class HuntGlitchMiddleware:
       def __init__(self, get_response):
           self.get_response = get_response
   
       def __call__(self, request):
           return self.get_response(request)
   
       def process_exception(self, request, exception):
           settings.HUNTGLITCH_LOGGER.capture_exception(
               additional_data={
                   "path": request.path,
                   "method": request.method,
                   "user": str(request.user) if hasattr(request, 'user') else 'Anonymous'
               }
           )
           return None  # Let Django handle the exception normally
   ```

### Flask Projects

```python
# app.py
from flask import Flask, request
from huntglitch_python import HuntGlitchLogger

app = Flask(__name__)
logger = HuntGlitchLogger()

@app.errorhandler(Exception)
def handle_exception(e):
    logger.capture_exception(
        additional_data={
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url
        }
    )
    # Return your normal error response
    return "Internal Server Error", 500
```

### FastAPI Projects

```python
# main.py
from fastapi import FastAPI, Request, HTTPException
from huntglitch_python import HuntGlitchLogger

app = FastAPI()
logger = HuntGlitchLogger()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.capture_exception(
        additional_data={
            "path": request.url.path,
            "method": request.method,
            "client": str(request.client)
        }
    )
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Environment Variable Management

### For Different Environments

**Development (.env.development):**
```env
PROJECT_KEY=dev-project-key
DELIVERABLE_KEY=dev-deliverable-key
```

**Production (system environment):**
```bash
export PROJECT_KEY=prod-project-key
export DELIVERABLE_KEY=prod-deliverable-key
```

**Docker:**
```dockerfile
ENV PROJECT_KEY=your-project-key
ENV DELIVERABLE_KEY=your-deliverable-key
```

**Kubernetes:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: huntglitch-config
data:
  PROJECT_KEY: <base64-encoded-key>
  DELIVERABLE_KEY: <base64-encoded-key>
```

### Loading Environment Files

The package automatically searches for environment files in this order:
1. `.env` (current directory)
2. `.env.local` (current directory)
3. `~/.huntglitch.env` (home directory)

You can also explicitly load a specific file:
```python
from huntglitch_python.config import Config

# Load from specific file
Config.load_env_file('/path/to/your/.env')

# Then initialize logger
logger = HuntGlitchLogger()
```

## Best Practices

### 1. Initialize Once
```python
# Good: Initialize once at application startup
logger = HuntGlitchLogger()

# Use the same instance throughout your app
def function1():
    logger.capture_exception()

def function2():
    logger.send_log(...)
```

### 2. Use Silent Failures in Production
```python
# Production configuration
logger = HuntGlitchLogger(
    silent_failures=True,  # Don't crash app if logging fails
    retries=3,            # Retry failed requests
    timeout=10            # Reasonable timeout
)
```

### 3. Add Contextual Information
```python
try:
    process_user_order(user_id, order_id)
except Exception:
    logger.capture_exception(
        additional_data={
            "user_id": user_id,
            "order_id": order_id,
            "timestamp": datetime.now().isoformat(),
            "feature": "order_processing"
        },
        tags={"severity": "high", "component": "payment"}
    )
```

### 4. Use Appropriate Log Levels
```python
# Critical errors
logger.send_log(..., log_type="error")

# Business logic warnings
logger.send_log(..., log_type="warning")

# Debug information (development only)
if settings.DEBUG:
    logger.send_log(..., log_type="debug")
```

## Troubleshooting

### Common Issues

1. **Import Error:**
   ```
   ImportError: No module named 'huntglitch_python'
   ```
   Solution: Install the package: `pip install huntglitch-python`

2. **Configuration Error:**
   ```
   ConfigurationError: PROJECT_KEY is required
   ```
   Solution: Set environment variables or pass keys explicitly

3. **Silent Failures:**
   If logs aren't appearing, check:
   - Environment variables are set correctly
   - Network connectivity to the API
   - Enable logging to see error messages:
     ```python
     import logging
     logging.basicConfig(level=logging.DEBUG)
     ```

### Debug Mode

```python
# Enable debug logging to see what's happening
import logging
logging.basicConfig(level=logging.DEBUG)

logger = HuntGlitchLogger(
    silent_failures=False,  # Raise exceptions on failures
    timeout=30              # Longer timeout for debugging
)
```
