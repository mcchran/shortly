# logger definition
import inspect
import logging
from logging.config import dictConfig


def set_logger_level(level):
    """ Sets the debugging level along with any other logging
    formating information

    :param str level: the logging_level

    """
    level = level.upper()
    if level not in ["INFO", "DEBUG", "WARNING", "CRITICAL"]:
        raise ValueError

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                }
            },
            "root": {"level": level, "handlers": ["wsgi"]},
        }
    )


logger = logging.getLogger()


def decorate_debug_message(debug_operation):
    def powerfull_debug(message):
        message = message or "No info"
        func = inspect.currentframe().f_back.f_code
        return debug_operation(
            "%s: %s in %s:%i"
            % (message, func.co_name, func.co_filename, func.co_firstlineno)
        )

    return powerfull_debug


logger.debug = decorate_debug_message(logger.debug)
logger.error = decorate_debug_message(logger.error)
