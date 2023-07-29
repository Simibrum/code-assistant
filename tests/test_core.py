'''"""
This module contains test functions for the `agent.core` module. It includes tests for the
`generate_tests`, `generate_module_docstrings`, and `format_modules` functions.

The `generate_tests` function tests the `generate_tests` function in the `agent.core` module.
It mocks various functions and methods to simulate the generation of tests for Python files.

The `generate_module_docstrings` function tests the `generate_module_docstrings` function in the
`agent.core` module. It mocks the necessary functions and methods to simulate the generation of
docstrings for Python modules.

The `format_modules` function tests the `format_modules` function in the `agent.core` module.
It mocks the necessary functions and methods to simulate the formatting of Python modules.

These test functions ensure the correct behavior and functionality of the `agent.core` module.
"""
'''
import ast
import logging
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest

import agent.core

logger = logging.getLogger(__name__)


def test_generate_tests():
    """
    Test the generate_tests function in agent.core
    """
    with patch(
        "agent.core.utils.get_python_files", return_value=["file1.py", "file2.py"]
    ), patch(
        "agent.core.utils.extract_functions_from_file",
        return_value=[("func1", "code1"), ("func2", "code2")],
    ), patch(
        "agent.core.os.path.exists", return_value=True
    ), patch(
        "agent.core.llm.generate_test", return_value=("test_code", "imports")
    ), patch(
        "agent.core.utils.add_imports"
    ), patch(
        "agent.core.open", new_callable=MagicMock
    ):
        agent.core.generate_tests()
        agent.core.utils.get_python_files.assert_called_once()
        agent.core.utils.extract_functions_from_file.assert_called()
        agent.core.os.path.exists.assert_called()
        agent.core.llm.generate_test.assert_called()
        agent.core.utils.add_imports.assert_called()
        agent.core.open.assert_called()


def test_generate_module_docstrings(mocker):
    """
    Test the function generate_module_docstrings.
    """
    mock_get_python_files = mocker.patch(
        "agent.core.utils.get_python_files", return_value=["file1.py", "file2.py"]
    )
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data="def function(): pass")
    )
    mock_ast_parse = mocker.patch(
        "agent.core.ast.parse", return_value=ast.parse("def function(): pass")
    )
    mock_get_docstring = mocker.patch(
        "agent.core.ast.get_docstring", side_effect=[None, "Existing docstring"]
    )
    mock_llm_generate_module_docstring = mocker.patch(
        "agent.core.llm.generate_module_docstring", return_value="Generated docstring"
    )
    mock_format_code = mocker.patch(
        "agent.core.utils.format_code", return_value="Formatted code"
    )
    agent.core.generate_module_docstrings()
    mock_get_python_files.assert_called_once()
    assert mock_open.call_count == 4
    assert mock_ast_parse.call_count == 2
    assert mock_get_docstring.call_count == 2
    assert mock_llm_generate_module_docstring.call_count == 1
    assert mock_format_code.call_count == 1


def test_format_modules(mocker):
    """
    Test the function format_modules from the core module.
    """
    mocker.patch(
        "agent.core.utils.get_python_files", return_value=["file1.py", "file2.py"]
    )
    mocker.patch("agent.core.utils.format_code", return_value="formatted_code")
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("agent.core.logger")
    agent.core.format_modules()
    agent.core.utils.get_python_files.assert_called_once_with(skip_tests=False)
    agent.core.utils.format_code.assert_any_call("")
    agent.core.logger.info.assert_any_call("Formatting module %s", "file1.py")
    agent.core.logger.info.assert_any_call("Formatting module %s", "file2.py")


def test_get_task_description(mocker):
    """Test the get_task_description function."""
    mocker.patch("builtins.input", return_value="Test task description")
    mocker.patch("agent.core.logger")

    assert agent.core.get_task_description() == "Test task description"


def test_generate_function_for_task():
    """Tests the function generate_function_for_task in agent/core.py."""
    with mock.patch("agent.core.llm.generate_code") as mock_generate_code, mock.patch(
        "agent.core.logger.debug"
    ) as mock_logger_debug, mock.patch(
        "agent.core.utils.add_imports"
    ) as mock_add_imports, mock.patch(
        "builtins.open", new_callable=mock.mock_open
    ) as mock_file:
        mock_generate_code.return_value = ("def function(): pass", "import numpy")
        agent.core.generate_function_for_task(
            "Create a function that adds two numbers", "./file.py")
        mock_generate_code.assert_called_once_with(
            "Create a function that adds two numbers", function_file="./file.py"
        )
        mock_logger_debug.assert_called_once_with(
            "Function code: %s", "def function(): pass"
        )
        mock_add_imports.assert_called_once_with("./file.py", "import numpy")
        mock_file.assert_called_once_with("./file.py", "a", encoding="utf-8")
        mock_file().write.assert_called_once_with("\ndef function(): pass\n")


def test_get_further_information(mocker):
    """Test the get_further_information function."""
    mocker.patch("builtins.input", side_effect=["Response 1", "Response 2"])
    mocker.patch("agent.core.logger.debug")
    questions = ["Question 1?", "Question 2?"]
    result = agent.core.get_further_information(questions)
    assert result == "Question 1?\nResponse 1\nQuestion 2?\nResponse 2\n"
