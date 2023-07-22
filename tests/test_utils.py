"""Tests for the utils module. """
import tempfile
import os
import utils


def test_extract_functions_from_file():
    """Test the extract_functions_from_file function."""
    # Define a simple Python code with two functions.
    code = '''
def func1(a, b):
    return a + b

def func2(x):
    return x * 2
'''

    # Create a temporary file and write the code to it.
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(code)
        temp_path = temp.name

    # Call extract_functions_from_file with the path of the temporary file.
    functions = utils.extract_functions_from_file(temp_path)

    # Check that the correct functions were extracted.
    assert len(functions) == 2
    assert (functions[0][0] == 'func1' and 'def func1(a, b):' in functions[0][1])
    assert (functions[1][0] == 'func2' and 'def func2(x):' in functions[1][1])

    # Cleanup: remove the temporary file.
    os.remove(temp_path)

def test_extract_project_description():
    # Test case with a valid README file
    assert utils.extract_project_description('README.md') == 'This is the project description.'

    # Test case with an invalid README file
    assert utils.extract_project_description('invalid.md') == ''

    # Test case with no Project Description section
    assert utils.extract_project_description('README_no_description.md') == ''

def test_read_requirements_txt():
    # Test if the function correctly reads the contents of the requirements.txt file
    contents = utils.read_requirements_txt()
    assert isinstance(contents, str)
    assert len(contents) > 0
    assert contents.startswith('# Code Generation Library')
    assert contents.endswith('pytest')
    # Test if the function correctly reads the contents of a custom file
    custom_file_path = 'custom_requirements.txt'
    custom_contents = utils.read_requirements_txt(file_path=custom_file_path)
    assert isinstance(custom_contents, str)
    assert len(custom_contents) > 0
    assert custom_contents.startswith('custom_package1')
    assert custom_contents.endswith('custom_package2')

def test_read_gitignore():
    # Test case 1: Test with empty .gitignore file
    gitignore_path = 'path/to/empty/.gitignore'
    expected_output = []
    assert utils.read_gitignore(gitignore_path) == expected_output
    
    # Test case 2: Test with non-empty .gitignore file
    gitignore_path = 'path/to/non_empty/.gitignore'
    expected_output = ['*.pyc', 'build/']
    assert utils.read_gitignore(gitignore_path) == expected_output

def test_should_use_file():
    # Test when ignore_patterns is None
    assert utils.should_use_file('path/to/file.txt', None) == True

    # Test when ignore_patterns is an empty list
    assert utils.should_use_file('path/to/file.txt', []) == True

    # Test when file matches an ignore pattern
    assert utils.should_use_file('path/to/file.txt', ['*.txt']) == False

    # Test when file does not match any ignore pattern
    assert utils.should_use_file('path/to/file.txt', ['*.py']) == True

    # Test when file is in git config directories
    assert utils.should_use_file('.git', ['*.py']) == False
    assert utils.should_use_file('.github', ['*.py']) == False
    assert utils.should_use_file('__pycache__', ['*.py']) == False
    assert utils.should_use_file('.pytest_cache', ['*.py']) == False

def test_build_directory_structure():
    # Test case 1: ...
    assert ...

    # Test case 2: ...
    assert ...

