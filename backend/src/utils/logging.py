import logging
from datetime import datetime
import json
from typing import Dict, Any


class SecurityLogger:
    """
    Comprehensive security logger for tracking security-related events.
    """

    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)

        # Create file handler for security logs
        if not self.logger.handlers:
            file_handler = logging.FileHandler("security.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_login_attempt(self, ip_address: str, user_email: str, success: bool, details: str = ""):
        """Log user login attempts."""
        event = {
            "event_type": "login_attempt",
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_email": user_email,
            "success": success,
            "details": details
        }
        self._log_security_event(event)

    def log_failed_auth(self, ip_address: str, user_identifier: str, auth_method: str, reason: str):
        """Log authentication failures."""
        event = {
            "event_type": "failed_authentication",
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_identifier": user_identifier,
            "auth_method": auth_method,
            "reason": reason
        }
        self._log_security_event(event)

    def log_unauthorized_access(self, ip_address: str, user_id: str, resource: str, action: str):
        """Log unauthorized access attempts."""
        event = {
            "event_type": "unauthorized_access",
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_id": user_id,
            "resource": resource,
            "action": action
        }
        self._log_security_event(event)

    def log_user_registration(self, ip_address: str, user_email: str):
        """Log user registration events."""
        event = {
            "event_type": "user_registration",
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": ip_address,
            "user_email": user_email
        }
        self._log_security_event(event)

    def log_privilege_change(self, user_id: str, changed_by: str, new_role: str, previous_role: str):
        """Log privilege changes."""
        event = {
            "event_type": "privilege_change",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "changed_by": changed_by,
            "new_role": new_role,
            "previous_role": previous_role
        }
        self._log_security_event(event)

    def log_data_access(self, user_id: str, resource: str, action: str, success: bool):
        """Log data access events."""
        event = {
            "event_type": "data_access",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "success": success
        }
        self._log_security_event(event)

    def _log_security_event(self, event: Dict[str, Any]):
        """Private method to log the security event."""
        self.logger.info(json.dumps(event))


# Create a singleton instance
security_logger = SecurityLogger()