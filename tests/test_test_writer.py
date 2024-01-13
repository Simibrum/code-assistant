import tempfile


def test_get_test_code(mocker):
    from code_management.test_writer import get_test_code

    mock_session = mocker.MagicMock()
    mock_result = mocker.MagicMock()
    mock_result.test_string = "sample_test_code"
    mocker.patch("code_management.test_writer.setup_db", return_value=mock_session)
    mocker.patch("code_management.test_writer.select", return_value=mocker.MagicMock())
    mock_session.execute.return_value.scalar_one.return_value = mock_result
    test_code = get_test_code(test_id=123)
    mock_session.execute.assert_called_once()
    assert test_code == "sample_test_code"


def test_get_function_code(mocker):
    from code_management.test_writer import get_function_code

    # Mock the session and CodeTest model
    mock_session = mocker.MagicMock()
    mock_result = mocker.MagicMock()
    mock_result.tested_function = "sample_function_code"

    # Define a function name that does not exist
    # non_existent_function_name = "non_existent_function"

    # Call the function with a non-existent function name
    mocker.patch("code_management.test_writer.setup_db", return_value=mock_session)
    mocker.patch("code_management.test_writer.select", return_value=mocker.MagicMock())

    mock_session.execute.return_value.scalar_one.return_value = mock_result

    function_code = get_function_code(test_id=123)

    # Assertions
    assert mock_session.execute.called
    assert function_code == "sample_function_code"
    assert (
        function_code is None
    ), "Function code should be None when the function does not exist"


def test_run_specific_test(mocker):
    import shutil

    from code_management.test_writer import run_specific_test

    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = "test output"
    (output, passed) = run_specific_test("test_module.py::test_function")
    pytest_path = shutil.which("pytest")
    mock_subprocess.assert_called_once_with(
        [pytest_path, "test_module.py::test_function"], capture_output=True, text=True
    )
    assert passed is True
    assert output == "test output"


def test_update_test_status(mocker):
    from code_management.test_writer import update_test_status

    mock_session = mocker.MagicMock()
    mock_result = mocker.MagicMock()
    mocker.patch("code_management.test_writer.setup_db", return_value=mock_session)
    mocker.patch("code_management.test_writer.select", return_value=mocker.MagicMock())
    mock_session.execute.return_value.scalar_one.return_value = mock_result
    mock_session.commit.return_value = None
    update_test_status(test_id=123, status="pass")
    mock_result.test_status = "pass"
    mock_session.commit.assert_called_once()


def test_replace_test_in_file():
    """Test the replace_test_in_file function."""
    from code_management.test_writer import replace_test_in_file

    original_content = "\ndef test_function_one():\n    assert True\n\ndef test_function_two():\n    assert False\n"
    new_test_content = "def test_function_two():\n    assert True\n"
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file_name = temp_file.name
        temp_file.write(original_content)
    assert replace_test_in_file(temp_file_name, "test_function_two", new_test_content)
    with open(temp_file_name, "r") as file:
        updated_content = file.read()
    expected_content = "\ndef test_function_one():\n    assert True\n\ndef test_function_two():\n    assert True\n\n\n"
    assert updated_content == expected_content
