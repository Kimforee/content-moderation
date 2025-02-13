import structlog
import logging

# Configure Structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

# Standard logging setup
logger = structlog.get_logger()

def log_info(message, **kwargs):
    """ Logs an info message """
    logger.info(message, **kwargs)

def log_error(message, **kwargs):
    """ Logs an error message """
    logger.error(message, **kwargs)
