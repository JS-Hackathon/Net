from enum import Enum

class RequirementPriority(str, Enum):
    CRITICAL = "CRITICAL"   # must_have
    HIGH = "HIGH"           # required
    MEDIUM = "MEDIUM"       # preferred
    LOW = "LOW"             # nice_to_have
