"""
Test the functions in code_reader.py.
"""
import os
from unittest import mock


from code_management import code_reader
from code_management.code_reader import (
    create_code_objects,
    handle_non_test_function_processing,
    FunctionInfo,
    ClassInfo,
)
from config import PROJECT_DIRECTORY


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
    mock_read_file_description.assert_called_once_with(
        "./code_management/code_reader.py"
    )
    assert result == {"./code_management/code_reader.py": "Test file description"}


def test_read_function_descriptions():
    """
    Test the function read_function_descriptions from code_reader.py.
    """
    test_file_path = os.path.join(PROJECT_DIRECTORY, "code_management/code_reader.py")
    function_descriptions = code_reader.read_function_descriptions(test_file_path)
    assert isinstance(function_descriptions, dict), "Result should be a dictionary."
    assert all(
        (isinstance(key, str) for key in function_descriptions)
    ), "All keys in the dictionary should be strings."
    print(function_descriptions)
    assert all(
        (
            isinstance(value, str) or value is None
            for value in function_descriptions.values()
        )
    ), "All values in the dictionary should be strings."
    assert (
        "read_function_descriptions" in function_descriptions
    ), "The function being tested should be in the returned dictionary."
    assert function_descriptions[
        "read_function_descriptions"
    ].startswith(
        "Read the descriptions of"
    ), "The description of the function being tested should start with its actual description."


def test_read_all_function_descriptions(mocker):
    """
    Test the function 'read_all_function_descriptions' from the 'code_reader.py' module.
    """
    mock_get_python_files = mocker.patch(
        "utils.get_python_files", return_value=["file1.py", "file2.py"]
    )
    mock_read_function_descriptions = mocker.patch(
        "code_management.code_reader.read_function_descriptions",
        return_value={"func1": "description1", "func2": "description2"},
    )
    result = code_reader.read_all_function_descriptions("some_directory")
    mock_get_python_files.assert_called_once_with("some_directory")
    assert mock_read_function_descriptions.call_args_list == [
        mocker.call("file1.py"),
        mocker.call("file2.py"),
    ]
    expected_result = {
        "file1.py": {"func1": "description1", "func2": "description2"},
        "file2.py": {"func1": "description1", "func2": "description2"},
    }
    assert result == expected_result


def test_generate_project_summary_prompt():
    """
    Test the function generate_project_summary_prompt in code_management/code_reader.py
    """
    code_file_descriptions = {
        "file1.py": "This is file1.",
        "file2.py": "This is file2.",
    }
    all_function_descriptions = {
        "file1.py": {
            "function1": "This is function1 in file1.",
            "function2": "This is function2 in file1.",
        },
        "file2.py": {"function1": "This is function1 in file2."},
    }
    result = code_reader.generate_project_summary_prompt(
        code_file_descriptions, all_function_descriptions
    )
    expected_result = "This project consists of several Python files, each with its own purpose, and several functions. The file 'file1.py' is described as: 'This is file1.'. The file 'file2.py' is described as: 'This is file2.'. In the file 'file1.py', there are several functions: The function 'function1' is described as: 'This is function1 in file1.'. The function 'function2' is described as: 'This is function2 in file1.'. In the file 'file2.py', there are several functions: The function 'function1' is described as: 'This is function1 in file2.'. Please provide a brief summary of the project as a whole."
    assert result == expected_result, f"Expected: {expected_result}, but got: {result}"


def test_get_summary():
    """Test the get_summary function."""
    with mock.patch(
        "code_management.code_reader.read_code_file_descriptions"
    ) as mock_read_code_file_descriptions, mock.patch(
        "code_management.code_reader.read_all_function_descriptions"
    ) as mock_read_all_function_descriptions, mock.patch(
        "code_management.code_reader.generate_project_summary_prompt"
    ) as mock_generate_project_summary_prompt, mock.patch(
        "code_management.code_reader.llm.generate_summary"
    ) as mock_llm_generate_summary:
        mock_read_code_file_descriptions.return_value = "code_file_descriptions"
        mock_read_all_function_descriptions.return_value = "all_function_descriptions"
        mock_generate_project_summary_prompt.return_value = "prompt"
        mock_llm_generate_summary.return_value = "summary"
        start_directory = "/path/to/directory"
        result = code_reader.get_summary(start_directory)
        mock_read_code_file_descriptions.assert_called_once_with(start_directory)
        mock_read_all_function_descriptions.assert_called_once_with(start_directory)
        mock_generate_project_summary_prompt.assert_called_once_with(
            "code_file_descriptions", "all_function_descriptions"
        )
        mock_llm_generate_summary.assert_called_once_with("prompt")
        assert result == "summary"


def test_create_code_objects(mocker):
    """
    Test the create_code_objects function to ensure it processes classes and functions.
    """
    import code_management.code_reader

    session_mock = mocker.MagicMock()
    file_path = "path/to/file.py"
    file_contents = "class TestClass:\n    pass\n\ndef test_func():\n    pass"
    mocker.patch("builtins.open", mocker.mock_open(read_data=file_contents))
    mocker.patch(
        "code_management.code_reader.extract_classes_and_functions",
        return_value=([("TestClass",)], [("test_func",)]),
    )
    mocker.patch("code_management.code_reader.handle_class_processing")
    mocker.patch("code_management.code_reader.handle_function_processing")
    mocker.patch("code_management.code_reader.link_tests")
    create_code_objects(session_mock, file_path)
    code_management.code_reader.extract_classes_and_functions.assert_called_once_with(
        file_contents
    )
    code_management.code_reader.handle_class_processing.assert_called_once_with(
        session_mock, ("TestClass",), file_path, file_contents
    )
    code_management.code_reader.handle_function_processing.assert_called_once_with(
        session_mock, ("test_func",), file_path
    )
    code_management.code_reader.link_tests.assert_called_once_with(session_mock)
    session_mock.commit.assert_called_once()


def test_handle_class_processing(mocker):
    """Test handle_class_processing function for managing class data."""

    from sqlalchemy.orm import Session
    from code_management.code_reader import handle_class_processing, ClassInfo

    mock_session = mocker.MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_filter_by = mock_query.filter_by.return_value
    mock_first = mock_filter_by.first
    class_params = ClassInfo(
        name="TestClass",
        source="class TestClass:",
        docstring='"""A test class."""',
        body=[],
        start_line=1,
        end_line=2,
    )
    file_path = "test_file.py"
    contents = 'class TestClass:\n    """A test class."""'
    mock_first.return_value = None

    handle_class_processing(mock_session, class_params, file_path, contents)

    assert mock_session.add.called
    assert mock_session.commit.called
    assert mock_session.refresh.called


def test_handle_function_in_class_processing(mocker):
    """Tests the handle_function_in_class_processing function for proper processing of
    CodeFunction objects within a class."""
    import code_management.code_reader

    mock_session = mocker.MagicMock()
    mock_node = mocker.MagicMock()
    mock_node.name = "test_function"
    mock_contents = "def test_function(): pass"
    mock_class_obj = mocker.MagicMock()
    mock_class_obj.functions = []
    mock_query = mock_session.query.return_value
    mock_filter_by = mock_query.filter_by.return_value
    mock_filter_by.first.return_value = None
    mocker.patch(
        "code_management.code_reader.ast.get_source_segment", return_value=mock_contents
    )
    mocker.patch("code_management.code_reader.ast.get_docstring", return_value="")
    code_management.code_reader.handle_function_in_class_processing(
        mock_session, mock_node, "path/to/file.py", mock_contents, mock_class_obj
    )
    mock_session.add.assert_called_once()


def test_handle_function_processing(mocker):
    """
    Test handle_function_processing to ensure it delegates to the correct handler.

    This test verifies that handle_function_processing correctly determines whether a
    function is a test function or not and calls the appropriate handler function
    based on the function name and file path provided.
    """
    from sqlalchemy.orm import Session
    import code_management.code_reader
    from code_management.code_reader import handle_function_processing, FunctionInfo

    mock_session = mocker.MagicMock(spec=Session)
    function_params = FunctionInfo(
        name="test_example",
        source="def test_example(): pass",
        docstring="Example test function",
        start_line=1,
        end_line=2,
    )
    file_path = "tests/test_example.py"
    mocker.patch("code_management.code_reader.handle_test_function_processing")
    mocker.patch("code_management.code_reader.handle_non_test_function_processing")
    handle_function_processing(mock_session, function_params, file_path)
    code_management.code_reader.handle_test_function_processing.assert_called_once_with(
        mock_session,
        function_params,
        "tests/test_example.py",
    )
    code_management.code_reader.handle_non_test_function_processing.assert_not_called()


def test_handle_test_function_processing(mocker):
    """
    Test handle_test_function_processing to ensure it creates a new CodeTest object and
    adds it to the session when an existing test is not found.
    """
    from unittest.mock import MagicMock

    from sqlalchemy.orm import Session

    from code_management.code_reader import (
        handle_test_function_processing,
        FunctionInfo,
    )

    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_filter_by = mock_query.filter_by.return_value
    mock_filter_by.first.return_value = None
    function_name = "new_test_function"
    function_string = "def new_test_function(): pass"
    file_path = "tests/test_new.py"
    function_doc_string = "This is a test function."
    function_params = FunctionInfo(
        name=function_name,
        source=function_string,
        docstring=function_doc_string,
        start_line=1,
        end_line=2,
    )
    handle_test_function_processing(mock_session, function_params, file_path)
    mock_session.add.assert_called_once()


def test_handle_non_test_function_processing(mocker):
    """Test handle_non_test_function_processing when the function does not exist."""
    session_mock = mocker.MagicMock()
    query_mock = session_mock.query.return_value
    filter_by_mock = query_mock.filter_by.return_value
    filter_by_mock.first.return_value = None
    code_function_mock = mocker.patch("code_management.code_reader.CodeFunction")
    function_name = "test_func"
    function_string = "def test_func(): pass"
    file_path = "some/file/path.py"
    function_doc_string = "Test function docstring."
    function_params = FunctionInfo(
        name=function_name,
        source=function_string,
        docstring=function_doc_string,
        start_line=1,
        end_line=2,
    )
    handle_non_test_function_processing(
        session=session_mock,
        function_params=function_params,
        file_path=file_path,
    )
    code_function_mock.assert_called_once_with(
        code_string=function_string,
        name=function_name,
        file_path=file_path,
        doc_string=function_doc_string,
        is_function=True,
    )
    session_mock.add.assert_called_once_with(code_function_mock.return_value)


def test_extract_classes_and_functions():
    from code_management.code_reader import extract_classes_and_functions

    dummy_code = '''
class DummyClass:
    """This is a dummy class."""
    def dummy_method(self):
        pass

def dummy_function():
    """This is a dummy function."""
    pass
'''
    expected_classes = [
        ClassInfo(
            name="DummyClass",
            source='class DummyClass:\n    """This is a dummy class."""\n    def dummy_method(self):\n        pass',
            docstring="This is a dummy class.",
            body=[],
            start_line=2,
            end_line=5,
        )
    ]
    expected_functions = [
        FunctionInfo(
            name="dummy_function",
            source='def dummy_function():\n    """This is a dummy function."""\n    pass',
            docstring="This is a dummy function.",
            start_line=7,
            end_line=9,
        )
    ]
    classes, functions = extract_classes_and_functions(dummy_code)
    assert classes[0].name == expected_classes[0].name
    assert classes[0].source == expected_classes[0].source
    assert classes[0].docstring == expected_classes[0].docstring
    assert classes[0].start_line == expected_classes[0].start_line
    assert classes[0].end_line == expected_classes[0].end_line
    assert functions == expected_functions


def test__is_test():
    """
    Test the _is_test function to ensure it correctly identifies test functions and files.
    """
    from code_management.code_reader import _is_test

    # Test cases where the function should return True
    assert _is_test("test_function", "some_file.py") is True
    assert _is_test("regular_function", "test_file.py") is True

    # Test cases where the function should return False
    assert _is_test("regular_function", "some_file.py") is False
    assert _is_test("testfunction", "some_file.py") is False

    # Test cases with mixed prefixes should still return True
    assert _is_test("test_function", "test_file.py") is True
