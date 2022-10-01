import atexit
import os
import sys
from typing import TYPE_CHECKING

__all__ = ["logger"]

if TYPE_CHECKING:
    from loguru import logger
else:
    from loguru._logger import Core, Logger

    # avoid using the global logger
    logger = Logger(
        core=Core(),
        exception=None,
        depth=0,
        record=False,
        lazy=False,
        colors=False,
        raw=False,
        capture=True,
        patcher=None,
        extra={},
    )

DEBUG = os.getenv("DEBUG", "0") in ("1", "true", "True", "yes")
DEFAULT_LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

# automatically log to stderr
# TODO: add file outputs
if sys.stderr:
    logger.add(sys.stderr, level=DEFAULT_LOG_LEVEL, backtrace=False)

atexit.register(logger.remove)

logger.debug("hi")
