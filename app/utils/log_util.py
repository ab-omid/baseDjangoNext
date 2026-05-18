import logging
from logging import Logger


"""
This module provides utility functions for working with the Python logging module.

The functions in this module are designed to be simple and straightforward,
and to provide a consistent interface for working with the logging module.

The main function provided by this module is get_logger(), which can be used
to retrieve a logger instance with a specific name. If no name is specified,
the root logger is returned.

Example usage:

import logging
from log_util import LogUtil

logger = LogUtil.get_logger()
logger.info("Hello, world!")

In this example, the get_logger() function is used to retrieve the root logger,
which is then used to log a message.

Note that this module is designed to be used as a helper module, and that
most users will not need to interact with it directly. Instead, they will
use the standard logging module directly.
"""


class LogUtil:
    """
    This class provides utility functions for working with the Python logging module.

    The functions in this class are designed to be simple and straightforward,
    and to provide a consistent interface for working with the logging module.

    The main function provided by this class is get_logger(), which can be used
    to retrieve a logger instance with a specific name. If no name is specified,
    the root logger is returned.

    Example usage:

    import logging
    from log_util import LogUtil

    logger = LogUtil.get_logger()
    logger.info("Hello, world!")

    In this example, the get_logger() function is used to retrieve the root logger,
    which is then used to log a message.

    Note that this class is designed to be used as a helper class and interface to global logging.
    """

    @staticmethod
    def get_logger(name: str | None = None) -> Logger:
        """
        Returns a logger instance with the specified name.

        If no name is specified, the root logger is returned.

        Args:
            name (str, optional): The name of the logger to retrieve. If not specified,
                the root logger is returned.

        Returns:
            Logger: The requested logger instance.
        """
        if name is None:
            return logging.getLogger("app.main")
        else:
            return logging.getLogger(name)
