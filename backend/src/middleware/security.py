from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response as StarletteResponse
from src.utils.logging import security_logger
from fastapi import HTTPException, status
from typing import List
import re


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> StarletteResponse:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


class SecurityValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate requests for security concerns.
    """

    def __init__(self, app, blocked_paths: List[str] = None, allowed_methods: List[str] = None):
        super().__init__(app)
        self.blocked_paths = blocked_paths or ["/etc/", "/proc/", "/dev/"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> StarletteResponse:
        # Check for dangerous paths
        path = request.url.path.lower()
        for blocked_path in self.blocked_paths:
            if blocked_path in path:
                security_logger.log_unauthorized_access(
                    ip_address=request.client.host if request.client else "unknown",
                    user_id="anonymous",
                    resource=path,
                    action="access"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden path"
                )

        # Validate HTTP method
        method = request.method.upper()
        if method not in self.allowed_methods:
            security_logger.log_unauthorized_access(
                ip_address=request.client.host if request.client else "unknown",
                user_id="anonymous",
                resource=path,
                action=method
            )
            raise HTTPException(
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                detail="Method not allowed"
            )

        # Check for potential SQL injection patterns in query parameters
        query_params_str = str(dict(request.query_params))
        if self._contains_sql_injection(query_params_str):
            security_logger.log_unauthorized_access(
                ip_address=request.client.host if request.client else "unknown",
                user_id="anonymous",
                resource=path,
                action="query_param"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potential SQL injection detected in query parameters"
            )

        response = await call_next(request)
        return response

    def _contains_sql_injection(self, text: str) -> bool:
        """
        Basic check for SQL injection patterns.
        In a production environment, you would use more sophisticated validation.
        """
        sql_patterns = [
            r"(?i)(union\s+select)",
            r"(?i)(drop\s+\w+)",
            r"(?i)(delete\s+from)",
            r"(?i)(insert\s+into)",
            r"(?i)(update\s+\w+\s+set)",
            r"(?i)(exec\s*\()",
            r"(?i)(script\s*:)",
            r"(?i)(alert\s*\()",
            r"(?i)(eval\s*\()",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text):
                return True
        return False


def add_security_middleware(app):
    """
    Function to add all security middlewares to the FastAPI app.
    """
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(SecurityValidationMiddleware)