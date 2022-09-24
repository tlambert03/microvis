from loguru._logger import Core, Logger
import atexit
import sys


__all__ = ["logger"]

logger = Logger(  # type: ignore
    core=Core(),  # type: ignore
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

if AUTOINIT and sys.stderr:
    logger.add(sys.stderr, level='INFO')  # type: ignore

atexit.register(logger.remove)
