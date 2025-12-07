"""
APE Benchmark Runner

Performance benchmarking infrastructure.
Measures reality without optimizing.

FUNDAMENTALS:
- Benchmarks measure reality, they don't improve it
- No caching added to improve numbers
- No code rewritten to "make benchmarks pass"
- Honest measurement of current baseline

Author: David Van Aelst
Version: 1.0.0
Status: ACTIVE - measures parse/link/runtime phases separately
"""

import time
import sys
import platform
import json
import statistics
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BenchmarkResult:
    """
    Result of a benchmark run.
    """
    name: str
    iterations: int
    total_time_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    std_dev_ms: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return asdict(self)
    
    def __str__(self):
        return (
            f"{self.name}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Average: {self.avg_ms:.3f}ms\n"
            f"  Min/Max: {self.min_ms:.3f}ms / {self.max_ms:.3f}ms\n"
            f"  Std dev: {self.std_dev_ms:.3f}ms"
        )


@dataclass
class BenchmarkEnvironment:
    """System environment information"""
    python_version: str
    platform: str
    machine: str
    processor: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        return asdict(self)


class BenchmarkRunner:
    """
    Benchmark runner for APE programs.
    
    PHILOSOPHY:
    - Measures current baseline, not optimized performance
    - Separate phase measurement (parse, link, runtime)
    - Multiple iterations for statistical significance
    - Honest reporting (no claims, just facts)
    
    Example:
        runner = BenchmarkRunner()
        result = runner.benchmark("test", lambda: expensive_op(), iterations=100)
        print(result)
    """
    
    def __init__(self, warmup_iterations: int = 3):
        """
        Initialize benchmark runner.
        
        Args:
            warmup_iterations: Number of warmup runs before timing
        """
        self._warmup_iterations = warmup_iterations
        self._results: List[BenchmarkResult] = []
    
    def benchmark(
        self, 
        name: str, 
        func: Callable[[], Any], 
        iterations: int = 100
    ) -> BenchmarkResult:
        """
        Run benchmark on a function.
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations to run
        
        Returns:
            BenchmarkResult with timing statistics
        """
        # Warmup runs (not timed)
        for _ in range(self._warmup_iterations):
            try:
                func()
            except Exception:
                pass  # Warmup failures ignored
        
        # Timed runs
        times_ms = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func()
            except Exception:
                pass  # Measure even if execution fails
            end = time.perf_counter()
            times_ms.append((end - start) * 1000)  # Convert to ms
        
        # Calculate statistics
        total_time_ms = sum(times_ms)
        avg_ms = total_time_ms / iterations
        min_ms = min(times_ms)
        max_ms = max(times_ms)
        std_dev_ms = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time_ms=total_time_ms,
            avg_ms=avg_ms,
            min_ms=min_ms,
            max_ms=max_ms,
            std_dev_ms=std_dev_ms
        )
        
        self._results.append(result)
        return result
    
    def compare(
        self, 
        implementations: Dict[str, Callable[[], Any]], 
        iterations: int = 100
    ) -> Dict[str, BenchmarkResult]:
        """
        Compare multiple implementations.
        
        Args:
            implementations: Dict of name -> function to benchmark
            iterations: Number of iterations per implementation
        
        Returns:
            Dict of name -> BenchmarkResult
        """
        results = {}
        for name, func in implementations.items():
            results[name] = self.benchmark(name, func, iterations)
        return results
    
    def get_environment(self) -> BenchmarkEnvironment:
        """Get system environment information"""
        return BenchmarkEnvironment(
            python_version=sys.version.split()[0],
            platform=platform.system(),
            machine=platform.machine(),
            processor=platform.processor() or "unknown"
        )
    
    def to_json(self, indent: int = 2) -> str:
        """
        Export results as JSON.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string with environment and benchmark results
        """
        data = {
            "environment": self.get_environment().to_dict(),
            "benchmarks": {
                result.name: result.to_dict() 
                for result in self._results
            }
        }
        return json.dumps(data, indent=indent)
    
    def save_json(self, filepath: str):
        """
        Save results to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        Path(filepath).write_text(self.to_json())
    
    def generate_report(self) -> str:
        """
        Generate human-readable benchmark report.
        
        Returns:
            Formatted report of all benchmark results
        """
        lines = []
        lines.append("=" * 60)
        lines.append("APE BENCHMARK REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        env = self.get_environment()
        lines.append(f"Environment:")
        lines.append(f"  Python: {env.python_version}")
        lines.append(f"  Platform: {env.platform} ({env.machine})")
        lines.append(f"  Processor: {env.processor}")
        lines.append("")
        
        lines.append("Results:")
        lines.append("")
        for result in self._results:
            lines.append(str(result))
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


__all__ = ['BenchmarkRunner', 'BenchmarkResult', 'BenchmarkEnvironment']


# CLI entry point for running benchmarks
if __name__ == "__main__":
    print("APE Benchmark Runner")
    print("Use run_benchmarks.py for full benchmark suite")
    print("This module provides the BenchmarkRunner infrastructure")
