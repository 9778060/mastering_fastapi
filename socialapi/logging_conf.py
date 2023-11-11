from logging.config import dictConfig
from .config import config, DevConfig

handlers = ["default", "rotating_file"]

def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(name)s:%(lineno)d - %(message)s"
                },
                "file": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(asctime)s %(msecs)03d %(levelname)s %(name)s %(lineno)d %(message)s"
                }           
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console"
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "socialapi.log",
                    "maxBytes": 1024,  # 1 KB
                    "backupCount": 2,
                    "encoding": "utf8"
                }
            },
            "loggers": {
                "uvicorn": {"handlers": handlers, "level": "INFO"},
                "socialapi": {
                    "handlers": handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False
                },
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "asyncpg": {"handlers": ["default"], "level": "WARNING"},                
            }
        }
    )