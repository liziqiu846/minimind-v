"""Private-module marginal encoded-bit value experiment framework."""

PROTOCOL_ID = "phase3-module-marginal-budget-v1"
PROTOCOL_VERSION = "phase3-module-budget-value-curve-sweep-v1"
MODULES = ("vision", "projector", "language")
CURVE_NAMES = {
    "vision": "R_V",
    "projector": "R_C",
    "language": "R_L",
}
SEED_PLACEHOLDER = "__FIXED_PROJECTION_SEED__"
STRUCTURE = "P"
