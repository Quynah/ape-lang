"""
Tests for executor: Ape task → LangChain tool execution.

NOTE: LangChain adapter uses file-based API (create_langchain_tool(file, function_name))
These tests are skipped - see ape-langchain examples for file-based usage.
"""

import pytest


@pytest.mark.skip(reason="LangChain uses file-based API, not ApeTask objects")
def test_langchain_api_difference():
    """
    LangChain integration uses:
        create_langchain_tool(ape_file: str, function_name: str)
    
    Not the ApeTask pattern used by Anthropic/OpenAI.
    See ape-langchain documentation for examples.
    """
    pass
