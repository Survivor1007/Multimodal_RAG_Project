import structlog
import logging
import os
from .config import settings

def setup_logging():
      """Config structures JSON logging"""

      timestampper = structlog.processors.TimeStamper(fmt="iso")

      processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            timestampper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
      ]

      structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
      )
      #====================================
      #Create the folder and file for logs
      #====================================
      log_file_path = os.path.join("logs", "app.log")
      os.makedirs("logs", exist_ok=True)

      #Root logger
      logging.basicConfig(
            format="%(message)s",
            level=settings.LOG_LEVEL,
            handlers=[ 
                      logging.FileHandler(log_file_path)],
      )

      #Uvicorn access logs
      logging.getLogger("uvicorn.access").handlers = []
      
