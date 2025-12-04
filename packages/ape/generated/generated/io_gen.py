from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Any
import datetime

from ape.runtime.core import RunContext

def io__read_line(prompt: str) -> str:
    """Auto-generated from Ape task 'read_line'.

    Constraints:
        - deterministic

    Steps:
        - display prompt if provided
        - read one line from standard input
        - return the line as a string
    """
    raise NotImplementedError

def io__write_file(path: str, content: str) -> bool:
    """Auto-generated from Ape task 'write_file'.

    Constraints:
        - deterministic

    Steps:
        - write content to file at path
        - return true
    """
    raise NotImplementedError

def io__read_file(path: str) -> str:
    """Auto-generated from Ape task 'read_file'.

    Constraints:
        - deterministic

    Steps:
        - read entire file from path
        - return content as string
    """
    raise NotImplementedError
