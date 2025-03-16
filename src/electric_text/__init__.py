from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("electric_text")
except PackageNotFoundError:
    __version__ = "unknown"
