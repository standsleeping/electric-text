from enum import Enum, auto


class ModelLoadError(Enum):
    NOT_FOUND = auto()
    IMPORT_ERROR = auto()
    NO_MODEL = auto()
    OTHER = auto()