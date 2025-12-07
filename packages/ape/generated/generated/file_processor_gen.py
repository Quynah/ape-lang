from __future__ import annotations
from dataclasses import dataclass

from ape.runtime.core import RunContext

@dataclass
class Stats:
    """Auto-generated from Ape entity 'Stats'."""
    count: int
    doubled_count: int

def file_processor__process_file(input_path: str, output_path: str) -> "Stats":
    """Auto-generated from Ape task 'process_file'.

    Constraints:
        - deterministic

    Steps:
        - call io . read_file with input_path to get content
        - count lines in content to get count
        - call math . multiply with count and 2 to get doubled_count
        - create Stats with count and doubled_count
        - call io . write_file with output_path and content
        - return stats
    """
    raise NotImplementedError

def file_processor__display_stats(stats: "Stats") -> bool:
    """Auto-generated from Ape task 'display_stats'.

    Constraints:
        - deterministic

    Steps:
        - convert stats to message
        - call sys . print with message
        - return success
    """
    raise NotImplementedError

def file_processor__interactive_demo(prompt_text: str) -> str:
    """Auto-generated from Ape task 'interactive_demo'.

    Constraints:
        - deterministic

    Steps:
        - call io . read_line with prompt_text
        - return user_input
    """
    raise NotImplementedError

FLOW_demo = {
    "name": "demo",
    "trigger": {},  # TODO: add trigger metadata
}

def file_processor__demo(context: RunContext) -> None:
    """Auto-generated from Ape flow 'demo'.

    Constraints:
        - deterministic

    Steps:
        - call interactive_demo with prompt
        - call process_file with paths
        - call display_stats with stats
        - call sys . print with completion message
    """
    # Flow steps:
    # 1. call interactive_demo with prompt
    # 2. call process_file with paths
    # 3. call display_stats with stats
    # 4. call sys . print with completion message
    raise NotImplementedError
