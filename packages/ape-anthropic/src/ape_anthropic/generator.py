"""
Natural language → Ape code generation via Claude.

Experimental feature for generating Ape task definitions from
natural language descriptions using Claude models.
"""

from typing import Optional, Any

# Optional import for Anthropic (only needed if using generation features)
try:
    import anthropic
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None  # type: ignore
    Anthropic = None  # type: ignore


def generate_ape_from_nl(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    api_key: Optional[str] = None
) -> str:
    """
    Generate Ape code from natural language description.

    Uses Anthropic's API to generate Ape task definitions from descriptions.
    This is an experimental feature.

    Args:
        prompt: Natural language description of the task
        model: Claude model to use (default: claude-3-5-sonnet-20241022)
        api_key: Anthropic API key (optional, uses environment variable if not provided)

    Returns:
        Generated Ape code as string

    Note:
        Requires `pip install ape-anthropic[anthropic]`
    """
    if not ANTHROPIC_AVAILABLE:
        raise ImportError(
            "Natural language generation requires the anthropic package. "
            "Install it with: pip install ape-anthropic[anthropic]"
        )

    # Initialize client
    client = Anthropic(api_key=api_key) if api_key else Anthropic()

    # System prompt for Ape code generation
    system_prompt = """You are an expert in the Ape programming language.

Ape is a deterministic AI-first programming language with the following syntax:

task task_name
  inputs:
    param_name: Type
  outputs:
    result_name: Type
  constraints:
    - constraint description
  steps:
    - step description

Types: String, Integer, Float, Boolean, List, Dict

Generate ONLY the Ape code, no explanations or markdown formatting.
Ensure all constraints are deterministic and all steps are explicit."""

    # Generate Ape code
    try:
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Generate Ape code for: {prompt}"}
            ]
        )

        generated_code = response.content[0].text

        # Clean up markdown code blocks if present
        if generated_code:
            generated_code = generated_code.strip()
            if generated_code.startswith("```"):
                # Remove code fences
                lines = generated_code.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                generated_code = "\n".join(lines)

        return generated_code or ""

    except Exception as e:
        raise Exception(f"Failed to generate Ape code: {e}") from e


def validate_generated_ape(code: str) -> tuple[bool, Optional[str]]:
    """
    Validate generated Ape code.

    Args:
        code: Ape code string

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for empty code
    if not code or not code.strip():
        return (False, "Empty code")

    try:
        from ape import compile as ape_compile
        from ape import ApeCompileError

        # Try to compile
        ape_compile(code)
        return (True, None)

    except ApeCompileError as e:
        return (False, str(e))
    except ImportError:
        return (False, "ape-lang not installed")
    except Exception as e:
        return (False, str(e))


def generate_and_compile_ape(
    prompt: str,
    model: str = "claude-3-5-sonnet-20241022",
    api_key: Optional[str] = None,
    max_retries: int = 3
) -> tuple[str, Any]:
    """
    Generate Ape code and compile it, with automatic retry on failure.

    Args:
        prompt: Natural language description
        model: Claude model to use
        api_key: Anthropic API key (optional)
        max_retries: Maximum number of generation attempts

    Returns:
        Tuple of (generated_code, compiled_module)
    """
    from ape import compile as ape_compile

    code = generate_ape_from_nl(prompt, model, api_key)

    for attempt in range(max_retries):
        is_valid, error = validate_generated_ape(code)

        if is_valid:
            module = ape_compile(code)
            return (code, module)

        # Retry with error feedback
        if attempt < max_retries - 1:
            feedback_prompt = f"{prompt}\n\nPrevious attempt failed with error: {error}\nPlease fix the code."
            code = generate_ape_from_nl(feedback_prompt, model, api_key)

    raise Exception(f"Failed to generate valid Ape code after {max_retries} attempts")


__all__ = [
    "generate_ape_from_nl",
    "validate_generated_ape",
    "generate_and_compile_ape",
]
