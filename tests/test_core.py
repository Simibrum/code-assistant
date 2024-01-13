"""
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
import ast
from unittest import mock
from unittest.mock import MagicMock, call, patch

import agent.core
import llm.llm_interface as llm
from agent.core import generate_test_from_function, populate_db
from functions import logger


def test_generate_tests():
    """
    Test the generate_tests function in agent.core
    """
    with patch(
        "agent.core.utils.get_python_files", return_value=["file1.py", "file2.py"]
    ), patch(
        "agent.core.utils.extract_functions_from_file",
        return_value=[("func1", "code1"), ("func2", "code2")],
    ), patch("agent.core.os.path.exists", return_value=True), patch(
        "agent.core.llm.generate_test", return_value=("test_code", "imports")
    ), patch("agent.core.utils.add_imports"), patch(
        "agent.core.open", new_callable=MagicMock
    ) as mock_open:
        agent.core.generate_tests()
        agent.core.utils.get_python_files.assert_called_once()
        agent.core.utils.extract_functions_from_file.assert_called()
        agent.core.os.path.exists.assert_called()
        agent.core.llm.generate_test.assert_called()
        agent.core.utils.add_imports.assert_called()
        mock_open.assert_called_with("tests/test_file2.py", "a", encoding="utf-8")
        mock_file = mock_open.return_value.__enter__.return_value
        expected_calls = [call("\n\n" + "test_code" + "\n\n")]
        mock_file.write.assert_has_calls(expected_calls)


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
    mocker.patch("builtins.open", mocker.mock_open(read_data="unformatted_code"))
    mocker.patch("agent.core.logger")
    agent.core.format_modules()
    agent.core.utils.get_python_files.assert_called_once_with(skip_tests=False)
    agent.core.utils.format_code.assert_any_call("unformatted_code")
    agent.core.logger.info.assert_any_call("Formatting module %s", "file1.py")
    agent.core.logger.info.assert_any_call("Formatting module %s", "file2.py")
    agent.core.logger.info.assert_any_call(
        "Writing formatted code to file %s", "file1.py"
    )
    agent.core.logger.info.assert_any_call(
        "Writing formatted code to file %s", "file2.py"
    )


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
        "agent.core.logger.info"
    ) as mock_logger_info, mock.patch(
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
        mock_logger_info.assert_called_once_with(
            "Writing imports to file: %s", "import numpy"
        )
        mock_add_imports.assert_called_once_with("./file.py", "import numpy")
        mock_file.assert_called_once_with("./file.py", "a", encoding="utf-8")
        mock_file().write.assert_called_once_with(("\ndef function(): pass\n"))


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
    mock_run_task = mocker.patch("agent.core.run_task", autospec=True)
    mock_generate_tests = mocker.patch("agent.core.generate_tests", autospec=True)
    mock_logger = mocker.patch("agent.core.logger", autospec=True)
    mock_issue = mock_gh_issues.return_value.get_next_issue.return_value
    mock_issue.number = 123
    agent.core.run_task_from_next_issue()
    mock_gh_issues.return_value.get_next_issue.assert_called_once()
    mock_gh_issues.return_value.task_from_issue.assert_called_once_with(mock_issue)
    mock_gh_issues.return_value.generate_branch_name.assert_called_once_with(mock_issue)
    mock_git_handler.return_value.create_new_branch.assert_called_once()
    mock_run_task.assert_called_once()
    mock_generate_tests.assert_called_once()
    mock_logger.info.assert_any_call("Running task from next issue.")
    mock_logger.debug.assert_any_call("Task description: %s")
    mock_logger.info.assert_any_call("Creating new branch for issue %s", 123)
    mock_logger.info.assert_any_call("Running task.")
    mock_logger.info.assert_any_call("Generating tests.")


def test_update_readme(mocker):
    """Test the update_readme function."""
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    mock_open().read.return_value = ""
    mock_update_readme_summary = mocker.patch(
        "agent.core.readme_manager.update_readme_summary"
    )
    mock_update_agent_structure = mocker.patch(
        "agent.core.readme_manager.update_agent_structure"
    )
    mock_update_readme_todos = mocker.patch(
        "agent.core.readme_manager.update_readme_todos"
    )
    agent.core.update_readme()
    assert mock_open.call_count == 3
    mock_update_readme_summary.assert_called_once()
    mock_update_agent_structure.assert_called_once()
    mock_update_readme_todos.assert_called_once()


def test_update_todos(mocker):
    """Test the update_todos function."""
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data="dummy readme text")
    )
    mock_update_readme_todos = mocker.patch(
        "code_management.readme_manager.update_readme_todos"
    )
    mock_update_readme_todos.return_value = "updated readme text"
    agent.core.update_todos()
    mock_open.assert_any_call("README.md", "r", encoding="utf-8")
    mock_open.assert_any_call("README.md", "w", encoding="utf-8")
    assert mock_open().read.call_count == 1
    assert mock_open().write.call_count == 1
    mock_open().write.assert_called_once_with("updated readme text")
    assert mock_update_readme_todos.call_count == 1
    mock_update_readme_todos.assert_called_once_with("dummy readme text")


def test_generate_test_from_function(mocker):
    """Test the generate_test_from_function function."""
    mock_function = mocker.Mock()
    mock_function.function_name = "test_function"
    mock_function.function_string = "def test_function(): pass"
    mock_function.file_path = "test_file_path"
    mocker.patch(
        "llm.llm_interface.generate_test", return_value=("test_code", "imports")
    )
    mocker.patch("functions.logger.info")
    test_name = "test_test"
    output = generate_test_from_function(mock_function, test_name)
    calls = [mocker.call("Generating test for function %s", "test_function")]
    logger.info.assert_has_calls(calls, any_order=True)
    llm.generate_test.assert_called_once_with(
        mock_function.function_string,
        function_file=mock_function.file_path,
        test_name=test_name,
    )
    assert output == ("test_code", "imports")
    mocker.patch("llm.llm_interface.generate_test", return_value=(None, "imports"))
    output = generate_test_from_function(mock_function, test_name)
    calls = [
        mocker.call("Generating test for function %s", "test_function"),
        mocker.call("Failed to generate test for function %s", "test_function"),
    ]
    logger.info.assert_has_calls(calls, any_order=True)
    llm.generate_test.assert_called_once_with(
        mock_function.function_string,
        function_file=mock_function.file_path,
        test_name=test_name,
    )
    assert output is None


def test_run_task(mocker):
    """Test the run_task function."""
    mocker.patch("agent.core.get_task_description", return_value="task description")
    mocker.patch(
        "agent.core.process_task",
        return_value=("generate_function_for_task", {"param1": "value1"}),
    )
    mocker.patch("agent.core.generate_function_for_task")
    mocker.patch("agent.core.get_further_information")
    mocker.patch("agent.core.logger")

    agent.core.run_task()
    agent.core.process_task.assert_called_once_with("task description")
    agent.core.generate_function_for_task.assert_called_once_with(param1="value1")
    agent.core.logger.debug.assert_any_call(
        "Function: %s", "generate_function_for_task"
    )
    agent.core.logger.debug.assert_any_call("Parameters: %s", {"param1": "value1"})

    agent.core.run_task("task description", 0, 3)
    agent.core.get_further_information.assert_called_once()

    agent.core.run_task("divide_and_process_sub_tasks", 0, 3)
    agent.core.process_task.assert_called_with("divide_and_process_sub_tasks")


def test_populate_db(mocker):
    """Test the populate_db function to ensure it correctly populates the database."""

    # Arrange
    mock_setup_db = mocker.patch("agent.core.setup_db")
    mock_get_python_files = mocker.patch("agent.core.utils.get_python_files")
    mock_get_python_files.return_value = ["test_file.py"]
    mock_create_code_objects = mocker.patch("agent.core.create_code_objects")
    mock_link_tests = mocker.patch("agent.core.link_tests")

    # Act
    populate_db(start_dir="test_dir")

    # Assert
    mock_setup_db.assert_called_once()
    mock_get_python_files.assert_called_once_with("test_dir", skip_tests=False)
    mock_create_code_objects.assert_called()
    mock_link_tests.assert_called_once()
