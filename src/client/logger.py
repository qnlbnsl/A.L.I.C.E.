import logging
import coloredlogs

# Create logger
logger = logging.getLogger("global_logger")
logger.setLevel(logging.DEBUG)

# create console handler with a debug level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# add the handler to logger
logger.addHandler(ch)

# ws_logger = logging.getLogger("websockets")
# ws_logger.setLevel(logging.DEBUG)
# ws_logger.addHandler(logging.StreamHandler())

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
coloredlogs.install(level="DEBUG", logger=logger, fmt=fmt, field_styles=field_styles)
