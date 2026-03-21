"""
Logging Middleware
Logs all API requests and responses
"""

import time
import logging
from fastapi import Request
from typing import Callable
import json

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable):
    """Log all requests and responses"""
    
    # Generate request ID
    request_id = str(time.time())
    
    # Log request
    logger.info(
        f"Request [{request_id}]: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Start timer
    start_time = time.time()
    
    # Process request
    try:
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response [{request_id}]: {response.status_code} "
            f"in {process_time:.4f}s"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error [{request_id}]: {str(e)} "
            f"after {process_time:.4f}s",
            exc_info=True
        )
        raise


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup application logging"""
    
    # Configure logging format
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    
    # Setup handlers
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )
    
    logger.info("Logging configured successfully")
