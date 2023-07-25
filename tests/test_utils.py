"""Tests for the utils module. """
import tempfile
import os
from unittest.mock import patch, mock_open
import utils


def test_extract_functions_from_file():
    """Test the extract_functions_from_file function."""
    code = "\ndef func1(a, b):\n    return a + b\n\ndef func2(x):\n    return x * 2\n"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
        temp.write(code)
        temp_path = temp.name
    functions = utils.extract_functions_from_file(temp_path)
    assert len(functions) == 2
    assert functions[0][0] == "func1" and "def func1(a, b):" in functions[0][1]
    assert functions[1][0] == "func2" and "def func2(x):" in functions[1][1]
    os.remove(temp_path)


def test_extract_project_description():
    """
    Test the extract_project_description function from the utils module.
    """
    assert "The aim is to build an agent" in utils.extract_project_description()
    assert utils.extract_project_description("invalid.md") == ""
    assert utils.extract_project_description("README_no_description.md") == ""


def test_read_requirements_txt():
    """
    Test the read_requirements_txt function from the utils module.
    """
    contents = utils.read_requirements_txt()
    assert isinstance(contents, str)
    assert len(contents) > 0
    assert contents.startswith("# Code Generation Library")
    assert contents.endswith("pytest-mock")
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
        temp.write("custom_package1\ncustom_package2\n")
        temp_path = temp.name
    custom_contents = utils.read_requirements_txt(file_path=temp_path)
    assert isinstance(custom_contents, str)
    assert len(custom_contents) > 0
    assert custom_contents.strip().startswith("custom_package1")
    assert custom_contents.strip().endswith("custom_package2")


def test_read_gitignore():
    """
    Test the read_gitignore function from the utils module.

    The test involves creating a temporary .gitignore file with some content, and then
    calling the read_gitignore function with the path to this file. The output of the function
    should match the content of the .gitignore file.
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
        temp_path = temp.name
    assert utils.read_gitignore(temp_path) == []
    gitignore_path = ".gitignore"
    expected_output = ["*.py[cod]", "build/"]
    read_file = utils.read_gitignore(gitignore_path)
    for pattern in expected_output:
        assert pattern in read_file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b"*.pyc\n.DS_Store")
        temp_path = temp.name
    try:
        gitignore_patterns = utils.read_gitignore(temp_path)
        assert gitignore_patterns == ["*.pyc", ".DS_Store"]
    finally:
        os.remove(temp_path)


def test_should_use_file():
    """
    Test the should_use_file() function from the utils module.
    """
    ignore_patterns = ["*.pyc", "*.tmp", "*~"]
    assert not utils.should_use_file("test.pyc", ignore_patterns)
    assert not utils.should_use_file("temp.tmp", ignore_patterns)
    assert not utils.should_use_file("file~", ignore_patterns)
    assert utils.should_use_file("test.py", ignore_patterns)
    assert utils.should_use_file("test.py")
    assert utils.should_use_file("path/to/file.txt", None) is True
    assert utils.should_use_file("path/to/file.txt", []) is True
    assert utils.should_use_file("path/to/file.txt", ["*.txt"]) is False
    assert utils.should_use_file("path/to/file.txt", ["*.py"]) is True
    assert utils.should_use_file(".git", ["*.py"]) is False
    assert utils.should_use_file(".github", ["*.py"]) is False
    assert utils.should_use_file("__pycache__", ["*.py"]) is False
    assert utils.should_use_file(".pytest_cache", ["*.py"]) is False


def test_build_directory_structure():
    """
    Test the build_directory_structure function from the utils module.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.mkdir(os.path.join(tmpdirname, "subdir"))
        with open(os.path.join(tmpdirname, "file.txt"), "w", encoding="utf-8") as file:
            file.write("Hello, world!")
        with open(
            os.path.join(tmpdirname, "subdir", "subfile.txt"), "w", encoding="utf-8"
        ) as file:
            file.write("Hello, world!")
        structure = utils.build_directory_structure(tmpdirname)
        print(structure)
        assert structure in [
            "file.txt\nsubdir\n  subfile.txt\n",
            "subdir\n  subfile.txt\nfile.txt\n",
        ]


def test_add_imports():
    """
    Test the add_imports function.

    The function should add new import statements to a Python file, avoiding duplicates.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".py") as tmp:
        tmp.write("import os\n")
        file_path = tmp.name
    try:
        utils.add_imports(file_path, ["import sys"])
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()
            assert "import sys" in contents
        utils.add_imports(file_path, ["import sys"])
        with open(file_path, "r", encoding="utf-8") as file:
            assert file.read().count("import sys") == 1
        utils.add_imports(file_path, ["import math", "import json"])
        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()
            assert "import math" in contents
            assert "import json" in contents
    finally:
        os.remove(file_path)


def test_format_code():
    """
    Test the format_code function.
    """
    code = "def test():\n    return 1"
    expected_result = "def test():\n    return 1\n"
    assert utils.format_code(code) == expected_result


def test_get_python_files():
    """
    Test the get_python_files function.

    This test checks if the get_python_files function correctly returns the paths of all
    Python files in the current directory, excluding the 'tests' directory.
    """
    python_files = utils.get_python_files()
    assert isinstance(python_files, list)
    for file in python_files:
        assert file.endswith(".py")
        assert "tests" not in file


def test_read_file_description() -> None:
    """
    Test the read_file_description function from the utils module.
    """
    expected_docstring = "\nThis is a test file.\nThis is the file's docstring.\n"
    with patch("builtins.open", new=mock_open(read_data=expected_docstring)):
        output_docstring = utils.read_file_description("test_path.py")
    assert output_docstring == expected_docstring, "The docstrings do not match."


def test_read_function_description():
    """
    Test the functionality of read_function_description.
    """
    test_func = (
        "def test_func():\n    '''\n"
        "    This is a test function.\n    '''\n    pass\n"
    )
    docstring = utils.read_function_description(test_func)
    assert docstring == "This is a test function."


def test_get_function_code():
    """
    Test get_function_code function from utils.py.

    The test will:
    - Write a temporary Python file with a known function.
    - Use get_function_code to extract the function.
    - Verify that the extracted function matches the known function.
    """
    known_function_code = 'def known_function():\n    return "Known function."'
    with open("temp.py", "w", encoding="utf-8") as file:
        file.write(known_function_code)
    try:
        extracted_function_code = utils.get_function_code("temp.py", "known_function")
        assert (
            extracted_function_code == known_function_code
        ), f"Expected:\n{known_function_code}\nBut got:\n{{extracted_function_code}}"
    finally:
        os.remove("temp.py")


def test_add_docstring_to_function():
    """
    Test the function add_docstring_to_function.
    """
    # Setup
    file_path = 'temp.py'
    function_name = 'test_func'
    docstring = 'This is a test function.'
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(f'def {function_name}():\n    pass')

    # Exercise
    utils.add_docstring_to_function(file_path, function_name, docstring)

    # Verify
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()
    assert lines[1].strip() == f'"""{docstring}"""'

    # Cleanup
    os.remove(file_path)
