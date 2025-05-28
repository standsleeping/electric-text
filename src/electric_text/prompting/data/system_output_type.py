from enum import Enum


class SystemOutputType(Enum):
    TEXT = "TEXT"
    DATA = "DATA"
    TOOL_CALL = "TOOL_CALL"
