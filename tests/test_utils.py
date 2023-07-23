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
    assert "The aim is to build an agent" in utils.extract_project_description('README.md')

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
    # Create a new temporary file with custom contents
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write('custom_package1\ncustom_package2\n')
        temp_path = temp.name
    # Test if the function correctly reads the contents of a custom file
    custom_contents = utils.read_requirements_txt(file_path=temp_path)
    assert isinstance(custom_contents, str)
    assert len(custom_contents) > 0
    assert custom_contents.startswith('custom_package1')
    assert custom_contents.endswith('custom_package2')

def test_read_gitignore():
    # Test case 1: Test with empty .gitignore file
    # Generate a temporary file with no contents
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp_path = temp.name
    # Call the function to read the .gitignore file
    assert utils.read_gitignore(temp_path) == []
    
    # Test case 2: Test with non-empty .gitignore file
    gitignore_path = '.gitignore'
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

import re

def test_extract_project_description():
    # Create a temporary README file
    with open('README.md', 'w') as f:
        f.write('## Project Description\nThis is a test project')
    
    # Import the function from utils.py
    from utils import extract_project_description
    
    # Call the function
    description = extract_project_description()
    
    # Assert that the function has correctly extracted the project description
    assert description == 'This is a test project'
    
    # Remove the temporary README file
    import os
    os.remove('README.md')

def test_read_requirements_txt():
    """
    Test the function read_requirements_txt.

    This test checks if the function correctly reads the content of a requirements.txt file.
    """
    # Create a mock requirements.txt file
    mock_requirements = "# Code Generation Library\nopenai\n\n# Tools\ntiktoken\npathspec\n\n# Testing\npytest"
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(mock_requirements)

    # Import the function to be tested
    from utils import read_requirements_txt

    # Call the function and check if the output is correct
    assert read_requirements_txt() == mock_requirements

def test_read_gitignore():
    """
    Test the read_gitignore function from the utils module.

    The test involves creating a temporary .gitignore file with some content, and then
    calling the read_gitignore function with the path to this file. The output of the function
    should match the content of the .gitignore file.
    """
    import os
    from utils import read_gitignore
    import tempfile

    # Create temporary .gitignore file with some patterns
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b'*.pyc\n.DS_Store')
        temp_path = temp.name

    try:
        # Call the function with the path to the temporary .gitignore file
        gitignore_patterns = read_gitignore(temp_path)

        # Check that the returned list matches the content of the .gitignore file
        assert gitignore_patterns == ['*.pyc', '.DS_Store']
    finally:
        # Ensure the temporary file is deleted
        os.remove(temp_path)

def test_should_use_file():
    """
    Test the should_use_file() function from the utils module.
    """
    # Prepare a list of ignore patterns.
    ignore_patterns = ['*.pyc', '*.tmp', '*~']

    # Test a file that should be ignored based on the patterns.
    assert not utils.should_use_file('test.pyc', ignore_patterns)
    assert not utils.should_use_file('temp.tmp', ignore_patterns)
    assert not utils.should_use_file('file~', ignore_patterns)

    # Test a file that should not be ignored based on the patterns.
    assert utils.should_use_file('test.py', ignore_patterns)

    # Test without providing any ignore patterns. By default, it should not ignore any file.
    assert utils.should_use_file('test.py')

def test_build_directory_structure():
    """Test the build_directory_structure function."""

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create some files and directories in the temporary directory
        os.mkdir(os.path.join(tmpdirname, 'subdir'))
        with open(os.path.join(tmpdirname, 'file.txt'), 'w') as f:
            f.write('Hello, world!')
        with open(os.path.join(tmpdirname, 'subdir', 'subfile.txt'), 'w') as f:
            f.write('Hello, world!')

        # Build the directory structure
        structure = utils.build_directory_structure(tmpdirname)

        # Check that the structure is as expected
        assert structure == f'{tmpdirname}\n  file.txt\n  subdir\n    subfile.txt\n'

def extract_functions_from_file(file_path: str):
    """
    Extract the names and source code of all functions in a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list[tuple]: A list of tuples, where each tuple contains the function name and source code.
    """
    with open(file_path, 'r', encoding="utf-8") as file:
        source_code = file.read()

    # Parse the source code to an AST.
    module = ast.parse(source_code)

    # Extract all function definitions.
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]

    # Get the source code and name for each function.
    function_data = []
    for function in functions:
        function_code = ast.get_source_segment(source_code, function)
        function_data.append((function.name, function_code))

    return function_data

def test_add_imports():
    import os
    import ast
    # Create a temporary python file for testing
    test_file_path = 'test_file.py'
    with open(test_file_path, 'w') as file:
        file.write('import os\n')
    # Add imports
    utils.add_imports(test_file_path, ['import ast', 'from pathlib import Path'])
    with open(test_file_path, 'r') as file:
        module = ast.parse(file.read())
    # Check if the imports were added correctly
    assert 'import os' in ast.dump(module)
    assert 'import ast' in ast.dump(module)
    assert 'from pathlib import Path' in ast.dump(module)
    # Clean up
    os.remove(test_file_path)

