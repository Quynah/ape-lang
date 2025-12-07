from __future__ import annotations
from dataclasses import dataclass

from ape.runtime.core import RunContext

class Operation:
    """Auto-generated from Ape enum 'Operation'."""
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"

@dataclass
class CalculationRequest:
    """Auto-generated from Ape entity 'CalculationRequest'."""
    left: float
    right: float
    op: "Operation"

@dataclass
class CalculationResult:
    """Auto-generated from Ape entity 'CalculationResult'."""
    left: float
    right: float
    op: "Operation"
    result: float

def calculate(request: "CalculationRequest") -> "CalculationResult":
    """Auto-generated from Ape task 'calculate'.

    Constraints:
        - deterministic

    Steps:
        - check request operation type
        - if operation is add then compute left plus right
        - if operation is subtract then compute left minus right
        - if operation is multiply then compute left times right
        - if operation is divide then compute left divided by right
        - create CalculationResult with left and right and op from request
        - set result field to computed value
        - return result
    """
    raise NotImplementedError

FLOW_calculator_demo = {
    "name": "calculator_demo",
    "trigger": {},  # TODO: add trigger metadata
}

def calculator_demo(context: RunContext) -> None:
    """Auto-generated from Ape flow 'calculator_demo'.

    Constraints:
        - deterministic

    Steps:
        - create CalculationRequest with left equals 1 and right equals 2 and op equals add
        - call calculate task with the request
        - output the result to console
    """
    # Flow steps:
    # 1. create CalculationRequest with left equals 1 and right equals 2 and op equals add
    # 2. call calculate task with the request
    # 3. output the result to console
    raise NotImplementedError

