"""
This module contains a single test function, `test_add_function_to_file()`, 
which tests the functionality of the `add_function_to_file()` function from the 
`code_writer` module. The purpose of this function is to add a new function to a 
Python file based on a given task description. 

The test function uses a temporary file to simulate the target Python file. 
It then mocks the API request to the LLM interface and sets the return value to a 
JSON object containing the necessary function code and import statements. The 
`add_function_to_file()` function is then called with the temporary file path and the task description. 

Afterwards, the content of the temporary file is read and checked to ensure 
that the added function is present and that it starts with the "def" keyword. 

This test function serves as a regression test to verify that the 
`add_function_to_file()` function correctly adds the desired function to the target Python file.
"""
import tempfile
import json
from unittest.mock import patch
from code_management.code_writer import add_function_to_file


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
            add_function_to_file(temp_file.name, task_description)
        with open(temp_file.name, "r", encoding="utf-8") as file:
            content = file.read()
        assert "add_two_numbers" in content
        assert "def " in content
