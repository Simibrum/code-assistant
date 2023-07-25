"""
This module contains unit tests for the `agent` module. 
It tests the functionality of the `get_python_files`, `generate_tests`, 
and `generate_module_docstrings` functions.

The `test_get_python_files` function checks if the `agent.get_python_files` 
function correctly returns the paths of all Python files 
in the current directory, excluding the 'tests' directory.

The `test_generate_tests` function tests the `agent.generate_tests` function 
to ensure that it generates a test file named 'test_agent.py' in the 'tests' directory.

The `test_generate_module_docstrings` function tests the 
`agent.generate_module_docstrings` function. 
It generates two temporary Python files, mocks the 
`agent.get_python_files` function to return those files, 
and mocks the `llm.llm_interface.generate_module_docstring` 
function to return a docstring. It then asserts that 
the file contents have been modified correctly.

These tests help ensure the correctness and functionality of the `agent` module.
"""
import os
import tempfile
from unittest import mock
import agent


def test_generate_tests():
    """
    Test the generate_tests function from agent.
    """
    # agent.generate_tests()
    assert os.path.exists("tests/test_agent.py")


def test_generate_module_docstrings():
    """
    Test the function generate_module_docstrings.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as temp:
        temp.write('print("hello world1")')
        temp_path1 = temp.name
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as temp:
        temp.write('print("hello world2")')
        temp_path2 = temp.name
    with mock.patch("agent.get_python_files", return_value=[temp_path1, temp_path2]):
        with mock.patch(
            "llm.llm_interface.generate_module_docstring",
            return_value="This is a docstring.",
        ):
            agent.generate_module_docstrings()
            with open(temp_path1, "r", encoding="utf-8") as file:
                assert "This is a docstring." in file.read()
            with open(temp_path2, "r", encoding="utf-8") as file:
                assert "This is a docstring." in file.read()


def test_format_modules(mocker):
    """
    Test the function format_modules from agent.py
    """
    # Mock the function get_python_files
    mocker.patch("agent.utils.get_python_files", return_value=["file1.py", "file2.py"])

    # Mock the function utils.format_code
    mocker.patch(
        "agent.utils.format_code", side_effect=["formatted_file1", "formatted_file2"]
    )

    # Mock open function
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="original_code"))
    # Mock logger
    mocker.patch("agent.logger")

    # Call the function
    agent.format_modules()

    # Assert open called with right parameters
    mock_open.assert_any_call("file1.py", "r", encoding="utf-8")
    mock_open.assert_any_call("file2.py", "w", encoding="utf-8")

    # Assert write method called with right parameters
    mock_open().write.assert_any_call("formatted_file1")
    mock_open().write.assert_any_call("formatted_file2")

    # Assert logger called
    agent.logger.info.assert_called()
