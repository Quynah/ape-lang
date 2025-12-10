#!/usr/bin/env python3
"""
Test counting script for APE repository.

This script uses pytest discovery to count tests in each package,
ensuring README files display accurate, evidence-based test counts.

Usage:
    python scripts/count_tests.py

Output:
    JSON object with test counts per package and total
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Optional


def count_tests_in_path(path: str, cwd: Optional[str] = None) -> int:
    """
    Count tests in a given path using pytest --collect-only.
    
    Args:
        path: Relative path to test directory
        cwd: Working directory to run pytest from (optional)
        
    Returns:
        Number of collected tests, or 0 if discovery fails
    """
    try:
        result = subprocess.run(
            ["pytest", path, "--collect-only", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd
        )
        
        # Parse output for "N tests collected"
        for line in result.stdout.splitlines():
            if "test collected" in line or "tests collected" in line:
                # Extract number from "595 tests collected in 0.18s"
                parts = line.split()
                if parts and parts[0].isdigit():
                    return int(parts[0])
        
        return 0
    except Exception as e:
        print(f"Warning: Failed to count tests in {path}: {e}", file=sys.stderr)
        return 0


def main():
    """Discover and report test counts for all packages."""
    
    repo_root = Path(__file__).parent.parent
    
    # Define test paths with their working directories
    test_configs = [
        ("ape_core", "tests/", repo_root / "packages" / "ape"),
        ("anthropic", "tests/", repo_root / "packages" / "ape-anthropic"),
        ("openai", "tests/", repo_root / "packages" / "ape-openai"),
        ("langchain", "tests/", repo_root / "packages" / "ape-langchain")
    ]
    
    # Count tests
    counts = {}
    for name, test_path, working_dir in test_configs:
        counts[name] = count_tests_in_path(test_path, cwd=str(working_dir))
    
    # Calculate total
    counts["total"] = sum(counts.values())
    
    # Output as JSON
    print(json.dumps(counts, indent=2))
    
    # Summary to stderr for human readability
    print("\n=== Test Count Summary ===", file=sys.stderr)
    print(f"APE Core:          {counts['ape_core']:4d}", file=sys.stderr)
    print(f"Anthropic Adapter: {counts['anthropic']:4d}", file=sys.stderr)
    print(f"OpenAI Adapter:    {counts['openai']:4d}", file=sys.stderr)
    print(f"LangChain Adapter: {counts['langchain']:4d}", file=sys.stderr)
    print(f"{'─' * 26}", file=sys.stderr)
    print(f"TOTAL:             {counts['total']:4d}", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
