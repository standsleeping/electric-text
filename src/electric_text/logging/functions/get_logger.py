import inspect
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with the specified name.

    If name is not provided, automatically infers the module name from the calling module.

    Args:
        name: The name for the logger, typically __name__ (optional)

    Returns:
        A configured logger instance
    """
    if name is None:
        # Inspect the call stack to get the module name of the calling module
        frame = inspect.currentframe()
        if frame:
            try:
                frame = frame.f_back
                if frame:
                    module = inspect.getmodule(frame)
                    if module:
                        name = module.__name__
            finally:
                # Always make sure to delete the frame reference to avoid reference cycles
                del frame

    # If we still don't have a name (unlikely), use a default
    if name is None:
        name = "electric_text"

    return logging.getLogger(name)
