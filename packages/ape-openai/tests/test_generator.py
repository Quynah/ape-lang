"""
Tests for generator: NL → Ape code via OpenAI.
Mirrors ape-anthropic generator tests for provider parity.
"""

import pytest
from unittest.mock import Mock, patch

from ape_openai.generator import (
    generate_ape_from_nl
)


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_success(mock_openai_class):
    """Test successful Ape code generation from natural language."""
    # Mock OpenAI API response
    mock_choice = Mock()
    mock_choice.message.content = """module main

fn add(a: Integer, b: Integer) -> Integer:
    constraints:
        a > 0
        b > 0
    steps:
        return a + b
"""

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_ape_from_nl("Create a function that adds two positive numbers")

    assert "module main" in result
    assert "fn add" in result
    assert "constraints:" in result
    assert "steps:" in result
    mock_client.chat.completions.create.assert_called_once()


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_custom_model(mock_openai_class):
    """Test generation with custom model."""
    mock_choice = Mock()
    mock_choice.message.content = "module test\n\nfn test():\n    steps:\n        pass"

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    generate_ape_from_nl("Create a test function", model="gpt-4")

    # Verify correct model was used
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4"


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_cleans_markdown(mock_openai_class):
    """Test that markdown code fences are properly removed."""
    mock_choice = Mock()
    mock_choice.message.content = '''```ape
module test

fn test():
    steps:
        pass
```'''

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_ape_from_nl("Test prompt")

    assert result.startswith("module test")
    assert "```" not in result


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_api_error(mock_openai_class):
    """Test handling of OpenAI API errors."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API Error: Rate limit exceeded")
    mock_openai_class.return_value = mock_client

    with pytest.raises(Exception, match="Failed to generate Ape code"):
        generate_ape_from_nl("Test prompt")


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_empty_response(mock_openai_class):
    """Test handling of empty response from OpenAI."""
    mock_choice = Mock()
    mock_choice.message.content = ""

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_ape_from_nl("Test prompt")

    # Should return empty string for empty content
    assert result == ""


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_with_api_key(mock_openai_class):
    """Test generation with explicit API key."""
    mock_choice = Mock()
    mock_choice.message.content = "module test"

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    generate_ape_from_nl("Test prompt", api_key="test-api-key")

    # Verify client was initialized with API key
    mock_openai_class.assert_called_once_with(api_key="test-api-key")


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_network_failure(mock_openai_class):
    """Test handling of network failures."""
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = ConnectionError("Network unreachable")
    mock_openai_class.return_value = mock_client

    with pytest.raises(Exception) as exc_info:
        generate_ape_from_nl("Test prompt")

    assert "Failed to generate Ape code" in str(exc_info.value)


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_strips_whitespace(mock_openai_class):
    """Test that leading/trailing whitespace is stripped."""
    mock_choice = Mock()
    mock_choice.message.content = "  module test  "

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    result = generate_ape_from_nl("Test prompt")

    assert result == "module test"
    assert not result.startswith(" ")
    assert not result.endswith(" ")


def test_generate_ape_from_nl_missing_openai():
    """Test error when openai package is not installed."""
    with patch('ape_openai.generator.OPENAI_AVAILABLE', False):
        with pytest.raises(ImportError, match="openai package"):
            generate_ape_from_nl("Test prompt")


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_uses_system_prompt(mock_openai_class):
    """Test that system prompt is included in API call."""
    mock_choice = Mock()
    mock_choice.message.content = "module test"

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    generate_ape_from_nl("Test prompt")

    # Verify system prompt was used
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]["messages"]
    assert any(msg.get("role") == "system" for msg in messages)
    assert any("Ape" in msg.get("content", "") for msg in messages if msg.get("role") == "system")


@patch('ape_openai.generator.OPENAI_AVAILABLE', True)
@patch('ape_openai.generator.OpenAI')
def test_generate_ape_from_nl_max_tokens(mock_openai_class):
    """Test that max_tokens is set appropriately."""
    mock_choice = Mock()
    mock_choice.message.content = "module test"

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client = Mock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client

    generate_ape_from_nl("Test prompt")

    # Verify max_tokens parameter
    call_args = mock_client.chat.completions.create.call_args
    assert "max_tokens" in call_args[1]
    assert call_args[1]["max_tokens"] == 2048
