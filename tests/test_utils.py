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
    """
    Test the extract_project_description function from the utils module.
    """
    # Test case with a valid README file
    assert "The aim is to build an agent" in utils.extract_project_description()

    # Test case with an invalid README file
    assert utils.extract_project_description('invalid.md') == ''

    # Test case with no Project Description section
    assert utils.extract_project_description('README_no_description.md') == ''


def test_read_requirements_txt():
    """
    Test the read_requirements_txt function from the utils module.
    """
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
    assert custom_contents.strip().startswith('custom_package1')
    assert custom_contents.strip().endswith('custom_package2')

def test_read_gitignore():
    """
    Test the read_gitignore function from the utils module.

    The test involves creating a temporary .gitignore file with some content, and then
    calling the read_gitignore function with the path to this file. The output of the function
    should match the content of the .gitignore file.
    """
    # Test case 1: Test with empty .gitignore file
    # Generate a temporary file with no contents
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp_path = temp.name
    # Call the function to read the .gitignore file
    assert utils.read_gitignore(temp_path) == []

    # Test case 2: Test with non-empty .gitignore file
    gitignore_path = '.gitignore'
    expected_output = ['*.py[cod]', 'build/']
    read_file = utils.read_gitignore(gitignore_path)
    for pattern in expected_output:
        assert pattern in read_file

    # Create temporary .gitignore file with some patterns
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b'*.pyc\n.DS_Store')
        temp_path = temp.name

    try:
        # Call the function with the path to the temporary .gitignore file
        gitignore_patterns = utils.read_gitignore(temp_path)

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
    # Test when ignore_patterns is None
    assert utils.should_use_file('path/to/file.txt', None) is True

    # Test when ignore_patterns is an empty list
    assert utils.should_use_file('path/to/file.txt', []) is True

    # Test when file matches an ignore pattern
    assert utils.should_use_file('path/to/file.txt', ['*.txt']) is False

    # Test when file does not match any ignore pattern
    assert utils.should_use_file('path/to/file.txt', ['*.py']) is True

    # Test when file is in git config directories
    assert utils.should_use_file('.git', ['*.py']) is False
    assert utils.should_use_file('.github', ['*.py']) is False
    assert utils.should_use_file('__pycache__', ['*.py']) is False
    assert utils.should_use_file('.pytest_cache', ['*.py']) is False

def test_build_directory_structure():
    """
    Test the build_directory_structure function from the utils module.
    """
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create some files and directories in the temporary directory
        os.mkdir(os.path.join(tmpdirname, 'subdir'))
        with open(os.path.join(
            tmpdirname, 'file.txt'), 'w', encoding="utf-8") as file:
            file.write('Hello, world!')
        with open(os.path.join(
            tmpdirname, 'subdir', 'subfile.txt'), 'w', encoding="utf-8") as file:
            file.write('Hello, world!')

        # Build the directory structure
        structure = utils.build_directory_structure(tmpdirname)
        print(structure)

        # Check that the structure is as expected
        assert structure == 'file.txt\nsubdir\n  subfile.txt\n'

def test_add_imports():
    """
    Test the add_imports function.

    The function should add new import statements to a Python file, avoiding duplicates.
    """
    # Create a temporary Python file.
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as tmp:
        tmp.write("import os\n")
        file_path = tmp.name

    try:
        # Test that the function adds a new import statement.
        utils.add_imports(file_path, ["import sys"])
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()
            assert "import sys" in contents

        # Test that the function avoids duplicates.
        utils.add_imports(file_path, ["import sys"])
        with open(file_path, "r", encoding="utf-8") as file:
            assert file.read().count("import sys") == 1

        # Test that the function can add multiple new import statements.
        utils.add_imports(file_path, ["import math", "import json"])
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()
            assert "import math" in contents
            assert "import json" in contents
    finally:
        # Delete the temporary file.
        os.remove(file_path)

test_add_imports()
