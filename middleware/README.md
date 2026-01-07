# Middleware Layer

This directory contains all middleware components for the Home Credit Loan Approval System:

## Contents

- **`auth.py`** - Authentication & authorization middleware (JWT tokens, role-based access)
- **`logging.py`** - Request/response logging middleware
- **`error_handler.py`** - Global error handling and formatting
- **`rate_limiter.py`** - API rate limiting middleware
- **`cors.py`** - CORS configuration middleware
- **`validation.py`** - Request validation middleware

## Usage

Middleware are applied in the backend FastAPI application in this order:

1. CORS - Allow cross-origin requests
2. Rate Limiter - Prevent API abuse
3. Logging - Log all requests
4. Authentication - Verify JWT tokens
5. Validation - Validate request payloads
6. Error Handler - Catch and format errors

## Authentication Flow

```
1. User sends request with Bearer token in Authorization header
2. Auth middleware validates token and extracts user info
3. User info is attached to request.state.user
4. Protected endpoints check user role/permissions
5. Audit log is created for sensitive actions
```

## Example Integration

```python
from fastapi import FastAPI
from middleware import (
    setup_cors,
    setup_auth,
    setup_logging,
    setup_rate_limiter,
    setup_error_handler
)

app = FastAPI()

# Apply middleware
setup_cors(app)
setup_rate_limiter(app)
setup_logging(app)
setup_auth(app)
setup_error_handler(app)
```
