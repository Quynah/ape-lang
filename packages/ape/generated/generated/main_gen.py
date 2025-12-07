from __future__ import annotations
from dataclasses import dataclass

from ape.runtime.core import RunContext

@dataclass
class Result:
    """Auto-generated from Ape entity 'Result'."""
    doubled: int
    powered: int

def main__main(value: int) -> "Result":
    """Auto-generated from Ape task 'main'.

    Constraints:
        - deterministic

    Steps:
        - call tools . double_value with value to get doubled
        - call tools . compute_power with value and 2 to get powered
        - create Result with doubled and powered
        - call tools . run_diagnostics with doubled
        - return result
    """
    raise NotImplementedError

FLOW_demo = {
    "name": "demo",
    "trigger": {},  # TODO: add trigger metadata
}

def main__demo(context: RunContext) -> None:
    """Auto-generated from Ape flow 'demo'.

    Constraints:
        - deterministic

    Steps:
        - set value to 5
        - call main with value
        - convert result to message
        - call sys . print with message
    """
    # Flow steps:
    # 1. set value to 5
    # 2. call main with value
    # 3. convert result to message
    # 4. call sys . print with message
    raise NotImplementedError
