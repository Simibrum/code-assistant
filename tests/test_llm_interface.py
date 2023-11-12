"""
This module provides a set of test functions to validate the functionality of the
`llm_interface` module in the `llm` package. The module includes tests for various
functions such as `load_json_string`, `api_request`, `generate_from_prompt`,
`generate_code`, `generate_test`, and `generate_module_docstring`. Each test function
is documented with clear and concise explanations of what it is testing.
"""
import json
from unittest import mock
from unittest.mock import MagicMock, patch

from llm import llm_interface


def test_load_json_string():
    """
    Test the load_json_string function.

    """
    correct_json = '{"key": "value"}'
    assert llm_interface.load_json_string(correct_json) == {"key": "value"}
    incorrect_json = '{"key": "\nvalue\n"}'
    try:
        llm_interface.load_json_string(incorrect_json)
    except json.JSONDecodeError:
        pass
    else:
        assert False, "Expected a JSONDecodeError"
    json_with_newline = '{"key": "value\\nmore value"}'
    assert llm_interface.load_json_string(json_with_newline) == {
        "key": "value\nmore value"
    }


def test_api_request():
    """
    Test the function api_request.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Translate this document into French."},
    ]
    functions = []
    function_call = None
    temperature = 0.5
    model = "gpt-3.5-turbo-0613"
    max_tokens = 10
    result = llm_interface.api_request(
        messages, functions, function_call, temperature, model, max_tokens
    )
    assert isinstance(result, dict)
    assert "choices" in result
    assert isinstance(result["choices"], list)


def test_generate_from_prompt():
    """Test the generate_from_prompt function."""
    prepare_prompt_func = MagicMock()
    prepare_prompt_args = {"arg1": "value1", "arg2": "value2"}
    prepare_prompt_func.return_value = "Test prompt"
    with patch("llm.llm_interface.api_request") as mock_api_request:
        mock_api_request.return_value = {
            "choices": [
                {
                    "message": {
                        "function_call": {
                            "arguments": json.dumps(
                                {
                                    "function_code": 'print("Hello World")',
                                    "import_statements": "import json",
                                }
                            )
                        }
                    }
                }
            ]
        }
        function_code, imports = llm_interface.generate_from_prompt(
            prepare_prompt_func, prepare_prompt_args
        )
        prepare_prompt_func.assert_called_once_with(arg1="value1", arg2="value2")
        assert function_code == 'print("Hello World")'
        assert imports == ["import json"]


def test_generate_code():
    """
    Test the generate_code function.
    """
    task_description = "Test task"
    function_file = "./llm/llm_interface.py"
    with patch("llm.llm_interface.api_request") as mock_api_request:
        mock_api_request.return_value = {
            "choices": [
                {
                    "message": {
                        "function_call": {
                            "arguments": json.dumps(
                                {
                                    "function_code": 'print("Hello World")',
                                    "import_statements": "import json",
                                }
                            )
                        }
                    }
                }
            ]
        }
        code, imports = llm_interface.generate_code(task_description, function_file)
    assert isinstance(code, str), f"Expected str, got {type(code).__name__}"
    assert isinstance(imports, list), f"Expected str, got {type(imports).__name__}"
    assert code == 'print("Hello World")'
    assert imports == ["import json"]


def test_generate_test():
    """
    Test the function generate_test from llm.llm_interface module.
    """
    function_code = 'def hello_world():\n    print("Hello, world!")'
    function_file = "./llm/llm_interface.py"
    with patch("llm.llm_interface.api_request") as mock_api_request:
        mock_api_request.return_value = {
            "choices": [
                {
                    "message": {
                        "function_call": {
                            "arguments": json.dumps(
                                {
                                    "function_code": 'print("Testing Hello World")',
                                    "import_statements": "import json",
                                }
                            )
                        }
                    }
                }
            ]
        }
        test_code, imports = llm_interface.generate_test(function_code, function_file)
    assert isinstance(test_code, str), f"Expected str, got {type(test_code).__name__}"
    assert isinstance(imports, list), f"Expected str, got {type(imports).__name__}"
    assert test_code == 'print("Testing Hello World")'
    assert imports == ["import json"]


def test_generate_module_docstring():
    """
    Test the generate_module_docstring function.
    """
    module_code = 'import os\n\ndef hello_world():\n    print("Hello, world!")\n'
    expected_docstring = (
        'A module that contains a hello_world function which prints "Hello, world!".'
    )
    with patch("llm.llm_interface.api_request") as mock_api_request:
        mock_api_request.return_value = {
            "choices": [
                {
                    "message": {
                        "content": 'A module that contains a hello_world function which prints "Hello, world!".'
                    }
                }
            ]
        }
        actual_docstring = llm_interface.generate_module_docstring(module_code)
    assert (
        actual_docstring == expected_docstring
    ), f"Expected: {expected_docstring}, but got: {actual_docstring}"


def test_generate_function_docstring():
    """
    Test for the function generate_function_docstring.
    """
    function_code = 'def hello_world():\n    print("Hello, World!")'
    expected_docstring = 'This function prints "Hello, World!" to the console.'
    with patch("llm.llm_interface.api_request") as mock_api_request:
        mock_api_request.return_value = {
            "choices": [{"message": {"content": expected_docstring}}]
        }
        docstring = llm_interface.generate_function_docstring(function_code)
        assert (
            docstring == expected_docstring
        ), f"Expected: {expected_docstring}, but got: {docstring}"


def test_generate_todo_list(mocker):
    """
    Test the generate_todo_list function.
    """
    mocker.patch(
        "llm.llm_interface.prompts.create_todo_list_prompt", return_value="prompt"
    )
    mocker.patch("llm.llm_interface.prompts.build_messages", return_value="messages")
    mocker.patch(
        "llm.llm_interface.api_request",
        return_value={"choices": [{"message": {"content": "content"}}]},
    )
    result = llm_interface.generate_todo_list()
    assert result == "content"


def test_generate_summary(mocker):
    """
    Test the generate_summary function.
    """
    mock_prompt = "This is a test prompt."
    mock_response = {"choices": [{"message": {"content": "This is a test summary."}}]}
    mocker.patch("llm.llm_interface.api_request", return_value=mock_response)
    result = llm_interface.generate_summary(mock_prompt)
    assert result == mock_response["choices"][0]["message"]["content"]


def test_reduce_module_descriptions():
    """Test the reduce_module_descriptions function."""
    initial_description = "This is the initial description."
    expected_output = "This is the reduced description."
    with mock.patch("llm.llm_interface.api_request") as mock_api_request:
        mock_api_request.return_value = {
            "choices": [{"message": {"content": expected_output}}]
        }
        actual_output = llm_interface.reduce_module_descriptions(initial_description)
        assert (
            actual_output == expected_output
        ), f"Expected: {expected_output}, but got: {actual_output}"


def test_review_issues(mocker):
    """Test the review_issues function."""

    # Arrange
    open_issues = ["issue1", "issue2", "issue3"]
    token_limit = 3800
    expected_issue_number = 1

    # Mock the dependencies
    mocker.patch(
        "llm.llm_interface.prompts.create_issue_review_prompt", return_value="prompt"
    )
    mocker.patch("llm.llm_interface.num_tokens_from_messages", return_value=3700)
    mocker.patch(
        "llm.llm_interface.api_request",
        return_value={
            "choices": [
                {"message": {"function_call": {"arguments": '{"issue_number": 1}'}}}
            ]
        },
    )
    mocker.patch(
        "llm.llm_interface.load_json_string",
        return_value={"issue_number": expected_issue_number},
    )
    mocker.patch("llm.llm_interface.logger")

    # Act
    result = llm_interface.review_issues(open_issues, token_limit)

    # Assert
    assert result == expected_issue_number
