"""Test the code_database module."""

import os
from code_management.code_database import setup_db
from code_management.code_database import CodeClass, CodeFunction


def test_setup_db(mocker):
    """Test the setup_db function."""
    # Mock the create_engine, sessionmaker and Session functions
    mock_create_engine = mocker.patch('code_management.code_database.create_engine')
    mock_sessionmaker = mocker.patch('code_management.code_database.sessionmaker')
    mock_Session = mocker.MagicMock()
    mock_sessionmaker.return_value = mock_Session

    # Import the setup_db function
    
    # Call the function
    db_path = 'sqlite:///test.db'
    setup_db(db_path)

    # Assert that create_engine was called with the default DB path
    mock_create_engine.assert_called_once_with('sqlite:///test.db', echo=True)

    # Assert that sessionmaker was called with the mocked engine
    mock_sessionmaker.assert_called_once_with(bind=mock_create_engine.return_value)

    # Assert that Session was called
    mock_Session.assert_called_once()

    # Delete the test database file
    os.remove('test.db')


def test_code_storage():
    """Test the storage of code in the database."""
    # Set up the test database
    db_path = 'sqlite:///test.db'
    session = setup_db(db_path)

    # Define the class and function strings
    class_name = "MyClass"
    class_string = "class MyClass: ..."
    function_name = "my_function"
    function_string = "def my_function(): ..."

    # Create and add a new class
    new_class = CodeClass(
        class_name=class_name, 
        class_string=class_string,
    )
    session.add(new_class)
    session.commit()  # Commit to get the new_class.id

    # Create and add a new function related to the class
    new_function = CodeFunction(
        function_name=function_name, 
        function_string=function_string, 
        class_id=new_class.id,
    )
    session.add(new_function)
    session.commit()

    # Query the database to verify the added class
    added_class = session.query(CodeClass).filter_by(class_name=class_name).first()
    assert added_class.class_name == class_name
    assert added_class.class_string == class_string

    # Query the database to verify the added function
    added_function = session.query(CodeFunction).filter_by(function_name=function_name).first()
    assert added_function.function_name == function_name
    assert added_function.function_string == function_string
    assert added_function.class_id == new_class.id

    # Close the session and delete the test database file
    session.close()
    os.remove('test.db')