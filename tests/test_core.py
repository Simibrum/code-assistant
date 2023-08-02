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
            "Create a function that adds two numbers", "./file.py"
        )
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

def test_run_task_from_next_issue(mocker):
    """Test the run_task_from_next_issue function."""
    mock_gh_issues = mocker.patch("agent.core.GitHubIssues", autospec=True)
    mock_git_handler = mocker.patch("agent.core.GitHandler", autospec=True)
    mock_logger = mocker.patch("agent.core.logger", autospec=True)
    mock_run_task = mocker.patch("agent.core.run_task", autospec=True)
    mock_generate_tests = mocker.patch("agent.core.generate_tests", autospec=True)
    mock_issue = mock_gh_issues.return_value.get_next_issue.return_value
    mock_issue.number = 123

    agent.core.run_task_from_next_issue()

    mock_gh_issues.return_value.get_next_issue.assert_called_once()
    mock_gh_issues.return_value.task_from_issue.assert_called_once_with(mock_issue)
    mock_gh_issues.return_value.generate_branch_name.assert_called_once_with(mock_issue)
    mock_git_handler.return_value.create_new_branch.assert_called_once()
    mock_run_task.assert_called_once()
    mock_generate_tests.assert_called_once()


def test_update_readme(mocker):
    """Test the update_readme function."""
    # Mock the open and read calls
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mock_open().read.return_value = ''

    # Mock the specific functions in readme_manager
    mock_update_readme_summary = mocker.patch("agent.core.readme_manager.update_readme_summary")
    mock_update_agent_structure = mocker.patch("agent.core.readme_manager.update_agent_structure")
    mock_update_readme_todos = mocker.patch("agent.core.readme_manager.update_readme_todos")

    # Call the function you're testing
    agent.core.update_readme()

    # Verify that the file was opened twice
    assert mock_open.call_count == 3

    # Verify that the functions were called with the correct arguments
    mock_update_readme_summary.assert_called_once()
    mock_update_agent_structure.assert_called_once()
    mock_update_readme_todos.assert_called_once()


def test_update_todos(mocker):
    """Test the update_todos function."""
    # Mock the open() function
    mock_open = mocker.patch('builtins.open', new_callable=mocker.mock_open)

    # Mock the readme_manager.update_readme_todos() function
    mock_update_readme_todos = mocker.patch(
        'code_management.readme_manager.update_readme_todos')

    # Call the function to test
    agent.core.update_todos()

    # Check that the file was opened twice
    assert mock_open.call_count == 2

    # Check that the update_readme_todos function was called once
    assert mock_update_readme_todos.call_count == 1
