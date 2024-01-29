import logging
from typing import Self
import coloredlogs
import os


class RelativePathFilter(logging.Filter):
    def filter(self: Self, record: logging.LogRecord) -> bool:
        record.relativePath = os.path.relpath(record.pathname.encode())
        return True


# Create logger
logging.getLogger().handlers.clear()
logger = logging.getLogger("memory_module")
logger.setLevel(logging.DEBUG)
logger.propagate = False
# create console handler with a debug level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# add the handler to logger
logger.addHandler(ch)
logger.addFilter(RelativePathFilter())

# Setting up format for coloredlogs
field_styles = coloredlogs.DEFAULT_FIELD_STYLES
field_styles.update(
    {
        "filename": {"color": "magenta"},
        "lineno": {"color": "green"},
        "funcName": {"color": "cyan"},
    }
)

# Create the desired format
fmt = "%(pathname)s:%(lineno)d: %(funcName)s: %(message)s"

# Install coloredlogs on the logger with the desired format
coloredlogs.install(level="DEBUG", logger=logger, fmt=fmt, field_styles=field_styles)  # type: ignore
