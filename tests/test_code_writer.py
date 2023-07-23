import tempfile
import json
from unittest.mock import patch
from code_management.code_writer import add_function_to_file

def test_add_function_to_file():
    """
    Test the add_function_to_file function.
    """
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.py') as temp_file:
        # Define a task description
        task_description = 'add two numbers'

        with patch('llm.llm_interface.api_request') as mock_api_request:
            mock_api_request.return_value = {
                'choices': [
                    {'message': {'function_call': {'arguments': json.dumps(
                {'function_code': 'def add_two_numbers(a,b):\n\t return a+b',
                 'import_statements': 'import json'}
                )}}}]}
            # Call the function
            add_function_to_file(temp_file.path, task_description)

        # Verify the content of the file
        with open(temp_file.path, 'r', encoding="utf-8") as file:
            content = file.read()
        assert 'add two numbers' in content
        assert 'def ' in content
