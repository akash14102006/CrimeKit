"""
Centralized structured logging configuration for CrimeKit.

Provides:
- JSON-formatted log output for production
- Human-readable colored output for development
- Correlation IDs for request tracing
- Agent execution IDs
- Audit log support
- Performance metrics logging
"""
import os
import sys
import json
import uuid
import time
import logging
import logging.handlers
from datetime import datetime, timezone
from typing import Optional
from contextvars import ContextVar

# Context variables for correlation tracking
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
agent_execution_id_var: ContextVar[str] = ContextVar('agent_execution_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter for production."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add correlation context
        corr_id = correlation_id_var.get('')
        if corr_id:
            log_entry["correlation_id"] = corr_id
        
        agent_id = agent_execution_id_var.get('')
        if agent_id:
            log_entry["agent_execution_id"] = agent_id
        
        uid = user_id_var.get('')
        if uid:
            log_entry["user_id"] = uid
        
        # Add exception info if present
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_entry["data"] = record.extra_data
        
        return json.dumps(log_entry, default=str)


class DevelopmentFormatter(logging.Formatter):
    """Human-readable colored formatter for development."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        corr_id = correlation_id_var.get('')
        corr_part = f" [{corr_id[:8]}]" if corr_id else ""
        
        timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
        return (
            f"{color}{timestamp} {record.levelname:<8}{self.RESET}"
            f"{corr_part} {record.name}: {record.getMessage()}"
        )


def get_log_level() -> str:
    """Get log level from environment."""
    return os.getenv('APP_LOG_LEVEL', 'info').upper()


def get_log_format() -> str:
    """Get log format from environment."""
    return os.getenv('APP_LOG_FORMAT', 'json' if os.getenv('APP_ENV') == 'production' else 'development')


def setup_logging() -> logging.Logger:
    """Configure and return the root logger."""
    level = get_log_level()
    fmt = get_log_format()
    
    root_logger = logging.getLogger('crimekit')
    root_logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    if fmt == 'json':
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(DevelopmentFormatter())
    
    handler.setLevel(getattr(logging, level, logging.INFO))
    root_logger.addHandler(handler)
    
    # File handler for production (with rotation)
    if os.getenv('APP_ENV') == 'production':
        log_dir = os.getenv('LOG_DIR', '/app/logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'crimekit.log'),
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(StructuredFormatter())
        file_handler.setLevel(getattr(logging, level, logging.INFO))
        root_logger.addHandler(file_handler)
        
        # Audit log (separate file)
        audit_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_dir, 'audit.log'),
            maxBytes=50 * 1024 * 1024,
            backupCount=30,
            encoding='utf-8'
        )
        audit_handler.setFormatter(StructuredFormatter())
        audit_handler.setLevel(logging.INFO)
        # Add audit logger
        audit_logger = logging.getLogger('crimekit.audit')
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
    
    # Suppress noisy libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(
        logging.INFO if os.getenv('APP_DEBUG') == 'true' else logging.WARNING
    )
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger under the crimekit namespace."""
    return logging.getLogger(f'crimekit.{name}')


def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())


def set_correlation_id(cid: str) -> None:
    """Set the current correlation ID."""
    correlation_id_var.set(cid)


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return correlation_id_var.get('')


def set_agent_execution_id(aid: str) -> None:
    """Set the current agent execution ID."""
    agent_execution_id_var.set(aid)


def set_user_id(uid: str) -> None:
    """Set the current user ID."""
    user_id_var.set(str(uid))


class AuditLogger:
    """Audit logging for security events."""
    
    def __init__(self):
        self.logger = logging.getLogger('crimekit.audit')
    
    def log_event(self, event_type: str, actor: str, target: str, 
                  action: str, detail: Optional[dict] = None, 
                  success: bool = True):
        """Log an audit event."""
        self.logger.info(
            f"AUDIT: {event_type}",
            extra={
                'extra_data': {
                    'event_type': event_type,
                    'actor': actor,
                    'target': target,
                    'action': action,
                    'success': success,
                    'detail': detail or {},
                    'correlation_id': get_correlation_id(),
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }
            }
        )


class PerformanceLogger:
    """Performance metrics logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f'crimekit.perf.{name}')
    
    def log_operation(self, operation: str, duration_ms: float, 
                      success: bool = True, metadata: Optional[dict] = None):
        """Log a performance measurement."""
        self.logger.info(
            f"PERF: {operation} completed in {duration_ms:.2f}ms",
            extra={
                'extra_data': {
                    'operation': operation,
                    'duration_ms': duration_ms,
                    'success': success,
                    'metadata': metadata or {},
                }
            }
        )


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation: str, logger: Optional[PerformanceLogger] = None):
        self.operation = operation
        self.logger = logger or PerformanceLogger('default')
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        success = exc_type is None
        self.logger.log_operation(
            self.operation, duration_ms, success,
            metadata={'exception': str(exc_val) if exc_val else None}
        )
        return False
