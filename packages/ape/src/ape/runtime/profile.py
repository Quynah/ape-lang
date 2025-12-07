"""
Ape Runtime Profiles

Predefined runtime configurations for common use cases.
Convenience layer over ExecutionContext and RuntimeExecutor settings.
"""

from typing import Any, Dict, List
from ape.runtime.context import ExecutionContext
from ape.runtime.trace import TraceCollector
from ape.errors import ProfileError


# Predefined runtime profiles
RUNTIME_PROFILES: Dict[str, Dict[str, Any]] = {
    "analysis": {
        "description": "Safe analysis mode - trace execution without mutations",
        "dry_run": True,
        "tracing": True,
        "capabilities": [],
        "max_iterations": 10_000,
    },
    "execution": {
        "description": "Full execution mode - run code with all capabilities",
        "dry_run": False,
        "tracing": False,
        "capabilities": ["*"],  # All capabilities
        "max_iterations": 10_000,
    },
    "audit": {
        "description": "Audit mode - trace with all capabilities but no mutations",
        "dry_run": True,
        "tracing": True,
        "capabilities": ["*"],  # All capabilities available for checking
        "max_iterations": 10_000,
    },
    "debug": {
        "description": "Debug mode - full tracing with limited iterations",
        "dry_run": False,
        "tracing": True,
        "capabilities": ["*"],
        "max_iterations": 1_000,  # Lower limit for debugging
    },
    "test": {
        "description": "Test mode - limited capabilities, tracing enabled",
        "dry_run": False,
        "tracing": True,
        "capabilities": ["io.stdout"],  # Only output allowed
        "max_iterations": 10_000,
    },
}


def get_profile(name: str) -> Dict[str, Any]:
    """
    Get runtime profile configuration by name.
    
    Args:
        name: Profile name (analysis, execution, audit, debug, test)
        
    Returns:
        Profile configuration dictionary
        
    Raises:
        ProfileError: If profile name is unknown
    """
    if name not in RUNTIME_PROFILES:
        available = ", ".join(RUNTIME_PROFILES.keys())
        raise ProfileError(
            message=f"Unknown profile '{name}'. Available: {available}",
            profile_name=name
        )
    
    return RUNTIME_PROFILES[name].copy()


def list_profiles() -> List[str]:
    """
    List all available profile names.
    
    Returns:
        List of profile names
    """
    return list(RUNTIME_PROFILES.keys())


def create_context_from_profile(profile_name: str) -> ExecutionContext:
    """
    Create ExecutionContext from profile.
    
    Args:
        profile_name: Name of profile to use
        
    Returns:
        ExecutionContext configured per profile
        
    Raises:
        ProfileError: If profile name is unknown
    """
    profile = get_profile(profile_name)
    
    # Create context with dry_run setting
    context = ExecutionContext(dry_run=profile["dry_run"])
    
    # Configure capabilities
    capabilities = profile["capabilities"]
    if capabilities == ["*"]:
        # Grant all built-in capabilities
        for cap in ["io.read", "io.write", "io.stdout", "io.stdin", "sys.exit"]:
            context.allow(cap)
    else:
        # Grant specific capabilities
        for cap in capabilities:
            context.allow(cap)
    
    return context


def create_executor_config_from_profile(profile_name: str) -> Dict[str, Any]:
    """
    Create RuntimeExecutor configuration from profile.
    
    Returns a dict of kwargs suitable for RuntimeExecutor.__init__().
    
    Args:
        profile_name: Name of profile to use
        
    Returns:
        Dictionary of executor configuration
        
    Raises:
        ProfileError: If profile name is unknown
    """
    profile = get_profile(profile_name)
    
    config = {
        "max_iterations": profile["max_iterations"],
        "dry_run": profile["dry_run"],
    }
    
    # Add trace collector if tracing enabled
    if profile["tracing"]:
        config["trace"] = TraceCollector()
    
    return config


def apply_profile_to_executor(executor: Any, profile_name: str) -> None:
    """
    Apply profile settings to existing RuntimeExecutor.
    
    Modifies executor in-place to match profile configuration.
    
    Args:
        executor: RuntimeExecutor instance to configure
        profile_name: Name of profile to apply
        
    Raises:
        ProfileError: If profile name is unknown
    """
    profile = get_profile(profile_name)
    
    # Update executor settings
    executor.max_iterations = profile["max_iterations"]
    executor.dry_run = profile["dry_run"]
    
    # Configure tracing
    if profile["tracing"]:
        if not executor.trace:
            executor.trace = TraceCollector()
    else:
        executor.trace = None


def get_profile_description(profile_name: str) -> str:
    """
    Get human-readable description of profile.
    
    Args:
        profile_name: Name of profile
        
    Returns:
        Description string
        
    Raises:
        ProfileError: If profile name is unknown
    """
    profile = get_profile(profile_name)
    return profile["description"]


def validate_profile(profile_config: Dict[str, Any]) -> None:
    """
    Validate profile configuration structure.
    
    Args:
        profile_config: Profile configuration to validate
        
    Raises:
        ProfileError: If configuration is invalid
    """
    required_keys = ["description", "dry_run", "tracing", "capabilities", "max_iterations"]
    
    for key in required_keys:
        if key not in profile_config:
            raise ProfileError(f"Profile missing required key: {key}")
    
    # Validate types
    if not isinstance(profile_config["dry_run"], bool):
        raise ProfileError("Profile 'dry_run' must be boolean")
    
    if not isinstance(profile_config["tracing"], bool):
        raise ProfileError("Profile 'tracing' must be boolean")
    
    if not isinstance(profile_config["capabilities"], list):
        raise ProfileError("Profile 'capabilities' must be list")
    
    if not isinstance(profile_config["max_iterations"], int):
        raise ProfileError("Profile 'max_iterations' must be integer")
    
    if profile_config["max_iterations"] <= 0:
        raise ProfileError("Profile 'max_iterations' must be positive")


def register_profile(name: str, config: Dict[str, Any]) -> None:
    """
    Register a custom runtime profile.
    
    Allows users to define their own profiles beyond the built-in ones.
    
    Args:
        name: Profile name (must be unique)
        config: Profile configuration dictionary
        
    Raises:
        ProfileError: If name already exists or config is invalid
    """
    if name in RUNTIME_PROFILES:
        raise ProfileError(f"Profile '{name}' already exists", profile_name=name)
    
    # Validate configuration
    validate_profile(config)
    
    # Register profile
    RUNTIME_PROFILES[name] = config.copy()


__all__ = [
    'RUNTIME_PROFILES',
    'get_profile',
    'list_profiles',
    'create_context_from_profile',
    'create_executor_config_from_profile',
    'apply_profile_to_executor',
    'get_profile_description',
    'validate_profile',
    'register_profile',
]
