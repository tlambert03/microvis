import atexit
import sys
import os

from loguru._logger import Core, Logger

__all__ = ["logger"]

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

AUTOINIT = True
DEFAULT_LOG_LEVEL = "DEBUG" if os.getenv("DEBUG") else "INFO"


if AUTOINIT and sys.stderr:
    logger.add(sys.stderr, level=DEFAULT_LOG_LEVEL, backtrace=False)

atexit.register(logger.remove)
