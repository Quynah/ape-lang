"""
LangChain chain integration for Ape.

Provides utilities for creating LangChain chains with Ape functions.
"""

from typing import Any, Optional, List
from pathlib import Path


def create_ape_chain(
    ape_file: str | Path,
    function_names: Optional[List[str]] = None,
    llm: Optional[Any] = None
) -> Any:
    """
    Create a LangChain chain with Ape tools.

    Args:
        ape_file: Path to .ape source file
        function_names: Optional list of function names to include (default: all)
        llm: Optional LangChain LLM instance

    Returns:
        LangChain chain with Ape tools

    Example:
        >>> from langchain.llms import OpenAI
        >>> llm = OpenAI()
        >>> chain = create_ape_chain("calc.ape", llm=llm)
        >>> result = chain.run("Add 5 and 3")
    """
    try:
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    except ImportError:
        raise ImportError(
            "Chain creation requires langchain. "
            "Install it with: pip install ape-langchain[langchain]"
        )

    from ape_langchain.tools import ApeLangChainTool
    from ape import compile as ape_compile, validate as ape_validate

    # Compile and validate Ape module
    module = ape_compile(ape_file)
    ape_validate(module)

    # Get all functions or specific ones
    if function_names is None:
        function_names = module.list_functions()

    # Create tools for each function
    tools = []
    for func_name in function_names:
        ape_tool = ApeLangChainTool(module, func_name)
        langchain_tool = ape_tool.as_structured_tool()
        tools.append(langchain_tool)

    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with access to deterministic Ape functions."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create agent
    if llm is None:
        raise ValueError("LLM instance is required for chain creation")

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


__all__ = [
    "create_ape_chain",
]
