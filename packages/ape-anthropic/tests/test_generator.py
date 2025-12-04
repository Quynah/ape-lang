"""
Tests for generator: NL  Ape code via Claude.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from ape_anthropic.generator import (
    generate_ape_from_nl
)


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_success(mock_anthropic_class):
    """Test successful Ape code generation from natural language."""
    # Mock Anthropic API response
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = """module main

fn add(a: Integer, b: Integer) -> Integer:
    constraints:
        a > 0
        b > 0
    steps:
        return a + b
"""

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = generate_ape_from_nl("Create a function that adds two positive numbers")

    assert "module main" in result
    assert "fn add" in result
    assert "constraints:" in result
    assert "steps:" in result
    mock_client.messages.create.assert_called_once()


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_custom_model(mock_anthropic_class):
    """Test generation with custom model."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = "module test\n\nfn test():\n    steps:\n        pass"

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    generate_ape_from_nl("Create a test function", model="claude-3-opus-20240229")

    # Verify correct model was used
    call_args = mock_client.messages.create.call_args
    assert call_args[1]["model"] == "claude-3-opus-20240229"


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_cleans_markdown(mock_anthropic_class):
    """Test that markdown code fences are properly removed."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = '''```ape
module test

fn test():
    steps:
        pass
```'''

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = generate_ape_from_nl("Test prompt")

    assert result.startswith("module test")
    assert "```" not in result


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_api_error(mock_anthropic_class):
    """Test handling of Anthropic API errors."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = Exception("API Error: Rate limit exceeded")
    mock_anthropic_class.return_value = mock_client

    with pytest.raises(Exception, match="Failed to generate Ape code"):
        generate_ape_from_nl("Test prompt")


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_empty_response(mock_anthropic_class):
    """Test handling of empty response from Claude."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = ""

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = generate_ape_from_nl("Test prompt")

    # Should return empty string for empty content
    assert result == ""


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_with_api_key(mock_anthropic_class):
    """Test generation with explicit API key."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = "module test"

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    generate_ape_from_nl("Test prompt", api_key="test-api-key")

    # Verify client was initialized with API key
    mock_anthropic_class.assert_called_once_with(api_key="test-api-key")


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_network_failure(mock_anthropic_class):
    """Test handling of network failures."""
    mock_client = Mock()
    mock_client.messages.create.side_effect = ConnectionError("Network unreachable")
    mock_anthropic_class.return_value = mock_client

    with pytest.raises(Exception) as exc_info:
        generate_ape_from_nl("Test prompt")

    assert "Failed to generate Ape code" in str(exc_info.value)


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_strips_whitespace(mock_anthropic_class):
    """Test that leading/trailing whitespace is stripped."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = "  module test  "

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    result = generate_ape_from_nl("Test prompt")

    assert result == "module test"
    assert not result.startswith(" ")
    assert not result.endswith(" ")


def test_generate_ape_from_nl_missing_anthropic():
    """Test error when anthropic package is not installed."""
    with patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', False):
        with pytest.raises(ImportError, match="anthropic package"):
            generate_ape_from_nl("Test prompt")


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_uses_system_prompt(mock_anthropic_class):
    """Test that system prompt is included in API call."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = "module test"

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    generate_ape_from_nl("Test prompt")

    # Verify system prompt was used
    call_args = mock_client.messages.create.call_args
    assert "system" in call_args[1]
    assert "Ape" in call_args[1]["system"]


@patch('ape_anthropic.generator.ANTHROPIC_AVAILABLE', True)
@patch('ape_anthropic.generator.Anthropic')
def test_generate_ape_from_nl_max_tokens(mock_anthropic_class):
    """Test that max_tokens is set appropriately."""
    mock_content = Mock()
    mock_content.type = "text"
    mock_content.text = "module test"

    mock_response = Mock()
    mock_response.content = [mock_content]

    mock_client = Mock()
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_class.return_value = mock_client

    generate_ape_from_nl("Test prompt")

    # Verify max_tokens parameter
    call_args = mock_client.messages.create.call_args
    assert "max_tokens" in call_args[1]
    assert call_args[1]["max_tokens"] == 2048
