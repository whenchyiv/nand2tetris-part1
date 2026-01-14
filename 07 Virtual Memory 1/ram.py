"""RAM mappings for the Hack VM language.

Author: Will Henchy
Date: 2025-10-12
"""

# Global memory mapping

REGISTERS_START: int = 0
REGISTERS_END: int = 15
SP: int = 0
LCL: int = 1
ARG: int = 2
THIS: int = 3
THAT: int = 4
TEMP: list[int] = [x for x in range(5, 9)]
R13: int = 13
R14: int = 14
R15: int = 15
STATIC: int = 16
NAMED_REGISTER_ADDRESSES: dict[str, int] = {
    "local": LCL,
    "argument": ARG,
    "pointer": THIS,  # Pointer base is THIS
    "this": THIS,
    "that": THAT,
    "temp": TEMP[0],
    "constant": SP,  # Constant commands push string to stack
    "r13": R13,
    "r14": R14,
    "r15": R15,
    "static": STATIC,
}
NAMED_REGISTER_NAMES: dict[str, str] = {
    "stackpointer": "SP",
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "constant": "SP",  # Constant commands push straight to the stack
    "temp": "TEMP",
    "r13": "R13",
    "r14": "R14",
    "r15": "R15",
}
STATIC_START: int = 16
STATIC_END: int = 255

STACK_START: int = 256
STACK_END: int = 2047
