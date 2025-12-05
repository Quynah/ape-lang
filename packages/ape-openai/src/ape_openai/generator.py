"""
Natural language → Ape code generation via OpenAI.

Experimental feature for generating Ape task definitions from
natural language descriptions using OpenAI models.
"""

from typing import Optional, Any

# Optional import for OpenAI (only needed if using generation features)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore


def generate_ape_from_nl(
    prompt: str,
    model: str = "gpt-4o",
    api_key: Optional[str] = None
) -> str:
    """
    Generate Ape code from natural language description.

    Uses OpenAI's API to generate Ape task definitions from descriptions.
    This is an experimental feature.

    Args:
        prompt: Natural language description of the task
        model: OpenAI model to use (default: gpt-4o)
        api_key: OpenAI API key (optional, uses environment variable if not provided)

    Returns:
        Generated Ape code as string

    Note:
        Requires `pip install ape-openai[openai]`
    """
    if not OPENAI_AVAILABLE:
        raise ImportError(
            "Natural language generation requires the openai package. "
            "Install it with: pip install ape-openai[openai]"
        )

    # Initialize client
    client = OpenAI(api_key=api_key) if api_key else OpenAI()

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
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate Ape code for: {prompt}"}
            ],
            temperature=0.0,  # Deterministic generation
        )

        generated_code = response.choices[0].message.content or ""

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

        return generated_code

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
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
    max_retries: int = 3
) -> tuple[str, Any]:
    """
    Generate Ape code and compile it, with automatic retry on failure.

    Args:
        prompt: Natural language description
        model: OpenAI model to use
        api_key: OpenAI API key (optional)
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
