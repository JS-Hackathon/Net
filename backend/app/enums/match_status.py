from enum import Enum

class MatchStatus(str, Enum):
    SATISFIED = "SATISFIED"
    PARTIAL = "PARTIAL"
    CLARIFICATION = "CLARIFICATION"
    MISSING = "MISSING"
