"""
Ape Runtime

Runtime execution support for Ape programs.
Includes both AST-based executor (sandbox-safe) and Python module integration.
"""

from ape.runtime.core import RunContext, FunctionSignature, ApeModule
from ape.runtime.context import ExecutionContext, ExecutionError, MaxIterationsExceeded
from ape.runtime.executor import RuntimeExecutor
from ape.runtime.trace import TraceCollector, TraceEvent, create_snapshot
from ape.runtime.explain import ExplanationStep, ExplanationEngine
from ape.runtime.replay import ReplayEngine
from ape.runtime.profile import (
    RUNTIME_PROFILES,
    get_profile,
    list_profiles,
    create_context_from_profile,
    create_executor_config_from_profile,
    apply_profile_to_executor,
    get_profile_description,
    validate_profile,
    register_profile,
)
# Import errors from unified hierarchy
from ape.errors import (
    ApeError,
    CapabilityError,
    ReplayError,
    ProfileError,
    RuntimeExecutionError,
    ParseError,
    ValidationError,
    LinkerError,
)

__all__ = [
    # Core runtime (Python integration)
    'RunContext',
    'FunctionSignature',
    'ApeModule',
    
    # AST-based executor (sandbox-safe)
    'ExecutionContext',
    'ExecutionError',
    'MaxIterationsExceeded',
    'RuntimeExecutor',
    
    # Execution tracing & observability
    'TraceCollector',
    'TraceEvent',
    'create_snapshot',
    
    # Capability gating
    'CapabilityError',
    
    # Explanation engine
    'ExplanationStep',
    'ExplanationEngine',
    
    # Replay engine
    'ReplayError',
    'ReplayEngine',
    
    # Runtime profiles
    'RUNTIME_PROFILES',
    'ProfileError',
    'get_profile',
    'list_profiles',
    'create_context_from_profile',
    'create_executor_config_from_profile',
    'apply_profile_to_executor',
    'get_profile_description',
    'validate_profile',
    'register_profile',
    
    # Errors (v1.0 unified hierarchy)
    'ApeError',
    'RuntimeExecutionError',
    'ParseError',
    'ValidationError',
    'LinkerError',
]

