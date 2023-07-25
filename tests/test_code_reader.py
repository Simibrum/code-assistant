"""
Test the functions in code_reader.py.
"""

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
    # Arrange
    test_file_path = './code_management/code_reader.py'

    # Act
    function_descriptions = code_reader.read_function_descriptions(test_file_path)

    # Assert
    assert isinstance(function_descriptions, dict), 'Result should be a dictionary.'
    assert all(isinstance(key, str) for key in function_descriptions), \
        'All keys in the dictionary should be strings.'
    print(function_descriptions)
    assert all(isinstance(value, str) for value in function_descriptions.values()), \
        'All values in the dictionary should be strings.'
    assert 'read_function_descriptions' in function_descriptions, \
        'The function being tested should be in the returned dictionary.'
    assert function_descriptions['read_function_descriptions'].startswith(
        'Read the descriptions of'), \
        'The description of the function being tested should start with its actual description.'
