"""
Test the functions in code_reader.py.
"""
from unittest import mock

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import Session, sessionmaker

from code_management import code_reader


def test_read_code_file_descriptions(mocker):
    """
    Test the function read_code_file_descriptions.

    Args:
        mocker (MockerFixture): Pytest fixture that allows you to mock python objects.
    """
    mock_get_python_files = mocker.patch("utils.get_python_files")
    mock_read_file_description = mocker.patch("utils.read_file_description")
    mock_get_python_files.return_value = ["./code_management/code_reader.py"]
    mock_read_file_description.return_value = "Test file description"
    result = code_reader.read_code_file_descriptions("./")
    mock_get_python_files.assert_called_once_with("./")
    mock_read_file_description.assert_called_once_with("./code_management/code_reader.py")
    assert result == {"./code_management/code_reader.py": "Test file description"}


def test_read_function_descriptions():
    """
    Test the function read_function_descriptions from code_reader.py.
    """
    test_file_path = "./code_management/code_reader.py"
    function_descriptions = code_reader.read_function_descriptions(test_file_path)
    assert isinstance(function_descriptions, dict), "Result should be a dictionary."
    assert all(
        (isinstance(key, str) for key in function_descriptions)
    ), "All keys in the dictionary should be strings."
    print(function_descriptions)
    assert all(
        (isinstance(value, str) for value in function_descriptions.values())
    ), "All values in the dictionary should be strings."
    assert (
        "read_function_descriptions" in function_descriptions
    ), "The function being tested should be in the returned dictionary."
    assert function_descriptions["read_function_descriptions"].startswith(
        "Read the descriptions of"
    ), "The description of the function being tested should start with its actual description."


def test_read_all_function_descriptions(mocker):
    """
    Test the function 'read_all_function_descriptions' from the 'code_reader.py' module.
    """
    mock_get_python_files = mocker.patch(
        "utils.get_python_files", return_value=["file1.py", "file2.py"]
    )
    mock_read_function_descriptions = mocker.patch(
        "code_management.code_reader.read_function_descriptions",
        return_value={"func1": "description1", "func2": "description2"},
    )
    result = code_reader.read_all_function_descriptions("some_directory")
    mock_get_python_files.assert_called_once_with("some_directory")
    assert mock_read_function_descriptions.call_args_list == [
        mocker.call("file1.py"),
        mocker.call("file2.py"),
    ]
    expected_result = {
        "file1.py": {"func1": "description1", "func2": "description2"},
        "file2.py": {"func1": "description1", "func2": "description2"},
    }
    assert result == expected_result


def test_generate_project_summary_prompt():
    """
    Test the function generate_project_summary_prompt in code_management/code_reader.py
    """
    code_file_descriptions = {"file1.py": "This is file1.", "file2.py": "This is file2."}
    all_function_descriptions = {
        "file1.py": {
            "function1": "This is function1 in file1.",
            "function2": "This is function2 in file1.",
        },
        "file2.py": {"function1": "This is function1 in file2."},
    }
    result = code_reader.generate_project_summary_prompt(
        code_file_descriptions, all_function_descriptions
    )
    expected_result = "This project consists of several Python files, each with its own purpose, and several functions. The file 'file1.py' is described as: 'This is file1.'. The file 'file2.py' is described as: 'This is file2.'. In the file 'file1.py', there are several functions: The function 'function1' is described as: 'This is function1 in file1.'. The function 'function2' is described as: 'This is function2 in file1.'. In the file 'file2.py', there are several functions: The function 'function1' is described as: 'This is function1 in file2.'. Please provide a brief summary of the project as a whole."
    assert result == expected_result, f"Expected: {expected_result}, but got: {result}"


def test_get_summary():
    """Test the get_summary function."""
    with mock.patch(
        "code_management.code_reader.read_code_file_descriptions"
    ) as mock_read_code_file_descriptions, mock.patch(
        "code_management.code_reader.read_all_function_descriptions"
    ) as mock_read_all_function_descriptions, mock.patch(
        "code_management.code_reader.generate_project_summary_prompt"
    ) as mock_generate_project_summary_prompt, mock.patch(
        "code_management.code_reader.llm.generate_summary"
    ) as mock_llm_generate_summary:
        mock_read_code_file_descriptions.return_value = "code_file_descriptions"
        mock_read_all_function_descriptions.return_value = "all_function_descriptions"
        mock_generate_project_summary_prompt.return_value = "prompt"
        mock_llm_generate_summary.return_value = "summary"
        start_directory = "/path/to/directory"
        result = code_reader.get_summary(start_directory)
        mock_read_code_file_descriptions.assert_called_once_with(start_directory)
        mock_read_all_function_descriptions.assert_called_once_with(start_directory)
        mock_generate_project_summary_prompt.assert_called_once_with(
            "code_file_descriptions", "all_function_descriptions"
        )
        mock_llm_generate_summary.assert_called_once_with("prompt")
        assert result == "summary"
