from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Any
import datetime

from ape.runtime.core import RunContext

def sys__print(message: str) -> bool:
    """Auto-generated from Ape task 'print'.

    Constraints:
        - deterministic

    Steps:
        - output message to standard output
        - return true
    """
    raise NotImplementedError

def sys__exit(code: int) -> bool:
    """Auto-generated from Ape task 'exit'.

    Constraints:
        - deterministic

    Steps:
        - terminate program with exit code
    """
    raise NotImplementedError
