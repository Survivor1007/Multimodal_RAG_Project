import structlog
import logging
import os
from .config import settings

def setup_logging():
      """Config structures JSON logging"""

      log_file_path = os.path.join("logs", "app.log")
      os.makedirs("logs", exist_ok=True)

      timestamper = structlog.processors.TimeStamper(fmt="%H:%M:%S")

      # ==== 🎨 Custom level styling ====
      def add_emoji(_, __, event_dict):
            level =event_dict.get("level", event_dict.get("level_name", "")).lower()

            emoji_map = {
                  "debug" : "🔍",
                  "info" : "✨",
                  "warning" : "⚠️",
                  "error" : "❌",
                  "critical" : "🔥"
            }

            event_dict["level_display"] = f"{emoji_map.get(level, '')} {level.upper()}"
            return event_dict

      def custom_console_renderer(_, __, event_dict):
            ts = event_dict.get("timestamp", "")
            level = event_dict.get("level_display", "")
            logger = event_dict.get("logger", "")
            msg = event_dict.get("event", "")

            return f"{level} | {ts} | {logger} | {msg}"
      
      def clean_event_dict(_, __, event_dict):
            event_dict.pop("level", None)
            return event_dict
      
      shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_emoji,
            timestamper,
            clean_event_dict,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
      ]
      structlog.configure(
            processors=shared_processors + [
                  structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
      )

      # Console formatter
      console_formatter = structlog.stdlib.ProcessorFormatter(
            processor=custom_console_renderer,
            foreign_pre_chain=shared_processors,
      )

      # File formatter
      file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
      )

      # === SETUP HANDLERS ===
      console_handler = logging.StreamHandler()
      console_handler.setFormatter(console_formatter)

      file_handler = logging.FileHandler(log_file_path)
      file_handler.setFormatter(file_formatter)

      #Root logger
      root_logger = logging.getLogger()
      if not root_logger.handlers:
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)

      root_logger.setLevel(settings.LOG_LEVEL)

      # logging.basicConfig(
      #       format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
      #       level=settings.LOG_LEVEL,
      #       handlers=[ 
      #             logging.FileHandler(log_file_path),
      #             logging.StreamHandler()
      #       ],        
      # )

      # ==== Reduce Noise from libraries ====
      logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
      logging.getLogger("sqlalchemy.engine").propagate = False

      logging.getLogger("transformers").setLevel(logging.ERROR)
      logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
      logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
      
      logging.getLogger("httpx").setLevel(logging.WARNING)
      logging.getLogger("httpcore").setLevel(logging.WARNING)

      logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
      for name in ["uvicorn", "uvicorn.error"]:
            uv_logger = logging.getLogger(name)
            uv_logger.handlers = []
            uv_logger.propagate = True
      #Uvicorn access logs
      # logging.getLogger("uvicorn.access").handlers = []


      