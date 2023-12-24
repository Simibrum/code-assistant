"""Test the code_database module."""
import os
from unittest.mock import create_autospec, Mock


from code_management.code_database import (
    CodeClass,
    CodeFunction,
    CodeTest,
    Session,
    add_test_to_db,
    link_tests,
    setup_db,
)


def test_setup_db(mocker):
    """Test the setup_db function."""
    mock_create_engine = mocker.patch("code_management.code_database.create_engine")
    mock_sessionmaker = mocker.patch("code_management.code_database.sessionmaker")
    mock_Session = mocker.MagicMock()
    mock_sessionmaker.return_value = mock_Session
    db_path = "sqlite:///test.db"
    setup_db(db_path)
    mock_create_engine.assert_called_once_with("sqlite:///test.db", echo=True)
    mock_sessionmaker.assert_called_once_with(bind=mock_create_engine.return_value)
    mock_Session.assert_called_once()
    if os.path.exists("test.db"):
        os.remove("test.db")


def test_code_storage():
    """Test the storage of code in the database."""
    db_path = "sqlite:///test.db"
    session = setup_db(db_path)
    class_name = "MyClass"
    class_string = "class MyClass: ..."
    function_name = "my_function"
    function_string = "def my_function(): ..."
    new_class = CodeClass(name=class_name, code_string=class_string)
    session.add(new_class)
    session.commit()
    new_function = CodeFunction(
        name=function_name,
        code_string=function_string,
        class_id=new_class.id,
    )
    session.add(new_function)
    session.commit()
    added_class = session.query(CodeClass).filter_by(name=class_name).first()
    assert added_class.name == class_name
    assert added_class.code_string == class_string
    added_function = session.query(CodeFunction).filter_by(name=function_name).first()
    assert added_function.name == function_name
    assert added_function.code_string == function_string
    assert added_function.class_id == new_class.id
    session.close()
    os.remove("test.db")


def test_link_tests(mocker):
    session = create_autospec(Session, instance=True)
    mock_function = create_autospec(CodeFunction, instance=True)
    mock_function.function_name = "mock_func"

    # Give a unique 'id' attribute to the mock_function object
    mock_function.id = 1

    mock_test = create_autospec(CodeTest, instance=True)
    mock_test.name = "test_mock_func"
    mock_test.class_test = False
    mock_test.function_id = None

    mock_class = create_autospec(CodeClass, instance=True)
    mock_class.name = "mock_class"  # Note this addition

    session.query(CodeClass).all.return_value = [mock_class]
    session.query(CodeTest).all.return_value = [mock_test]

    session.query(CodeFunction).filter_by(
        name="mock_func"
    ).first.return_value = mock_function

    with mocker.patch(
        "code_management.code_database.get_class_names", return_value=["mock_class"]
    ):
        link_tests(session)

    session.query(CodeTest).all.assert_called_once()
    session.query(CodeFunction).filter_by.assert_called_with(name="mock_func")

    # Assert mock_test.function_id equals the id of the returned function object
    assert mock_test.function_id == mock_function.id
    session.commit.assert_called_once()


def test_add_test_to_db(monkeypatch):
    """
    Test the add_test_to_db function to ensure it properly adds a test entry to the database.
    """

    def mock_compute_test_name(*args, **kwargs):
        return "test_example_function"

    monkeypatch.setattr(
        "code_management.code_database.compute_test_name", mock_compute_test_name
    )

    db_session_mock = Mock(spec=Session)
    function_mock = Mock(spec=CodeFunction)
    function_mock.id = 1
    function_mock.class_id = 2
    function_mock.name = "example_function"

    test_code = "assert True"
    test_file_name = "test_function.py"
    add_test_to_db(db_session_mock, function_mock, test_code, test_file_name)
    db_session_mock.add.assert_called_once()
    new_test = db_session_mock.add.call_args[0][0]
    assert new_test.code_string == test_code
    assert new_test.name == "test_example_function"
    assert new_test.file_path == test_file_name
    assert new_test.function_id == function_mock.id
    assert new_test.class_id == function_mock.class_id


def test_CodeClass___repr__():
    """
    Test the __repr__ method of the CodeClass.
    """

    # Creating instance of CodeClass
    code_class_instance = CodeClass()
    code_class_instance.id = 1
    code_class_instance.name = "TestClass"

    result = code_class_instance.__repr__()
    expected = "<CodeClass(1, TestClass)>"
    assert result == expected


def test_CodeFunction___repr__():
    """
    Test the __repr__ method of the CodeFunction class.
    """
    # Create a CodeFunction instance
    code_function_instance = CodeFunction()
    code_function_instance.id = 1
    code_function_instance.name = "test_function"

    result = repr(code_function_instance)
    expected_result = (
        f"<CodeFunction({code_function_instance.id}, {code_function_instance.name})>"
    )
    assert result == expected_result


def test_CodeTest___repr__():
    """Unit test for the __repr__ method of the CodeTest class."""
    test_instance = CodeTest(id=1, name="test_repr")
    result = test_instance.__repr__()
    expected_repr = "<CodeTest(1, test_repr)>"
    assert result == expected_repr, f"Expected repr: {expected_repr}, but got: {result}"
