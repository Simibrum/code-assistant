import ast
import logging
import os
from unittest import mock
from unittest.mock import MagicMock, patch

import black
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
    # Mock the utils.get_python_files function to return a specific list of files.
    mocker.patch('agent.core.utils.get_python_files', return_value=['file1.py', 'file2.py'])

    # Mock the utils.format_code function to return a formatted code.
    mocker.patch('agent.core.utils.format_code', return_value='formatted_code')

    # Mock the open function to prevent actual file reading and writing.
    mocker.patch('builtins.open', mocker.mock_open())

    # Mock the logger
    mocker.patch('agent.core.logger')

    # Call the function
    agent.core.format_modules()

    # Assert that the mocked functions were called with the expected arguments.
    agent.core.utils.get_python_files.assert_called_once_with(skip_tests=False)
    agent.core.utils.format_code.assert_any_call('')
    agent.core.logger.info.assert_any_call('Formatting module %s', 'file1.py')
    agent.core.logger.info.assert_any_call('Formatting module %s', 'file2.py')

