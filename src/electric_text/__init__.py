from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("electric_text")
except PackageNotFoundError:
    __version__ = "unknown"

# Export the main notebook-friendly interface
from electric_text.prompting import generate

__all__ = [
    "generate",
    "__version__",
]
