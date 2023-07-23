import os
import tempfile
from unittest import mock
import agent


def test_get_python_files():
    """
    Test the get_python_files function.

    This test checks if the get_python_files function correctly returns the paths of all
    Python files in the current directory, excluding the 'tests' directory.
    """
    python_files = agent.get_python_files()
    assert isinstance(python_files, list)
    for file in python_files:
        assert file.endswith('.py')
        assert 'tests' not in file

def test_generate_tests():
    """
    Test the generate_tests function from agent.
    """
    agent.generate_tests()
    assert os.path.exists('tests/test_agent.py')

def test_generate_module_docstrings():
    """
    Test the function generate_module_docstrings.
    """
    # Generate two temporary python files
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".py") as temp:
        temp.write('print("hello world1")')
        temp_path1 = temp.name
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".py") as temp:
        temp.write('print("hello world2")')
        temp_path2 = temp.name
    # Mock the function get_python_files to return a list of python files
    with mock.patch('agent.get_python_files', return_value=[temp_path1, temp_path2]):
        # Mock the function llm.generate_module_docstring to return a docstring
        with mock.patch(
            'llm.llm_interface.generate_module_docstring', 
            return_value='This is a docstring.'):
            # Call the function generate_module_docstrings
            agent.generate_module_docstrings()

            # Assert that the file contents have been modified
            # This is a simplified assertion. In a real test case, read the file
            # and check its contents.
            with open(temp_path1, 'r', encoding='utf-8') as file:
                assert 'This is a docstring.' in file.read()
            with open(temp_path2, 'r', encoding='utf-8') as file:
                assert 'This is a docstring.' in file.read()
