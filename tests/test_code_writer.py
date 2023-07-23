import tempfile
from code_management.code_writer import add_function_to_file

def test_add_function_to_file():
    """
    Test the add_function_to_file function.
    """
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix='.py') as temp_file:
        # Define a task description
        task_description = 'add two numbers'

        # Call the function
        add_function_to_file(temp_file.name, task_description)

        # Verify the content of the file
        with open(temp_file.name, 'r') as file:
            content = file.read()
        assert 'add two numbers' in content
        assert 'def ' in content

