"""
This module contains a single test function, `test_add_function_to_file()`, 
which tests the functionality of the `add_function_to_file()` function from the 
`code_writer` module. The purpose of this function is to add a new function to a 
Python file based on a given task description. 

The test function uses a temporary file to simulate the target Python file. 
It then mocks the API request to the LLM interface and sets the return value to a 
JSON object containing the necessary function code and import statements. The 
`add_function_to_file()` function is then called with the 
temporary file path and the task description. 

Afterwards, the content of the temporary file is read and checked to ensure 
that the added function is present and that it starts with the "def" keyword. 

This test function serves as a regression test to verify that the 
`add_function_to_file()` function correctly adds the desired function to the target Python file.
"""
import tempfile
import json
from unittest.mock import patch
import code_management.code_writer as code_writer


def test_add_function_to_file():
    """
    Test the add_function_to_file function.
    """
    with tempfile.NamedTemporaryFile(suffix=".py") as temp_file:
        task_description = "add two numbers"
        with patch("llm.llm_interface.api_request") as mock_api_request:
            mock_api_request.return_value = {
                "choices": [
                    {
                        "message": {
                            "function_call": {
                                "arguments": json.dumps(
                                    {
                                        "function_code": "def add_two_numbers(a,b):\n\t return a+b",
                                        "import_statements": "import json",
                                    }
                                )
                            }
                        }
                    }
                ]
            }
            code_writer.add_function_to_file(temp_file.name, task_description)
        with open(temp_file.name, "r", encoding="utf-8") as file:
            content = file.read()
        assert "add_two_numbers" in content
        assert "def " in content


def test_generate_function_docstring(mocker):
    """
    Test the generate_function_docstring function.
    """
    # Create a mock for the utils.get_function_code function.
    mock_get_function_code = mocker.patch(
        'utils.get_function_code', return_value='def test(): pass')

    # Create a mock for the llm.generate_function_docstring function.
    mock_generate_function_docstring = mocker.patch(
        'llm.generate_function_docstring', return_value='Test docstring')

    # Create a mock for the utils.add_docstring_to_function function.
    mock_add_docstring_to_function = mocker.patch('utils.add_docstring_to_function')

    # Call the function.
    code_writer.generate_function_docstring('path/to/file', 'test')

    # Assert that the mocked functions were called with the correct parameters.
    mock_get_function_code.assert_called_once_with('path/to/file', 'test')
    mock_generate_function_docstring.assert_called_once_with('def test(): pass')
    mock_add_docstring_to_function.assert_called_once_with('path/to/file', 'test', 'Test docstring')
