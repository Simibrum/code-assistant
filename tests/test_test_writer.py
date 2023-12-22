def test_get_test_code(mocker):
    from code_management.test_writer import get_test_code

    # Mock the session and CodeTest model
    mock_session = mocker.MagicMock()
    mock_result = mocker.MagicMock()
    mock_result.test_string = "sample_test_code"

    # Patching 'setup_db' to return the mock session
    mocker.patch("code_management.test_writer.setup_db", return_value=mock_session)

    # Instead of returning a string, 'select' should return a mock
    mocker.patch("code_management.test_writer.select", return_value=mocker.MagicMock())

    # Add a scalar_one attribute to the return_value of mock_session.execute
    mock_session.execute.return_value.scalar_one.return_value = mock_result

    # Call the function
    test_code = get_test_code(test_id=123)

    # Assertions
    mock_session.execute.assert_called_once()
    assert test_code == "sample_test_code"


def test_get_function_code(mocker):
    from code_management.test_writer import get_function_code

    # Mock the session and CodeTest model
    mock_session = mocker.MagicMock()
    mock_result = mocker.MagicMock()
    mock_result.tested_function = "sample_function_code"

    # Call the function
    mocker.patch("code_management.test_writer.setup_db", return_value=mock_session)
    mocker.patch("code_management.test_writer.select", return_value=mocker.MagicMock())

    mock_session.execute.return_value.scalar_one.return_value = mock_result

    function_code = get_function_code(test_id=123)

    # Assertions
    assert mock_session.execute.called
    assert function_code == "sample_function_code"


def test_run_specific_test(mocker):
    from code_management.test_writer import run_specific_test

    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = "test output"

    output, passed = run_specific_test("test_module.py::test_function")

    mock_subprocess.assert_called_once_with(
        ["pytest", "test_module.py::test_function"], capture_output=True, text=True
    )
    assert passed is True
    assert output == "test output"


def test_update_test_status(mocker):
    from code_management.test_writer import update_test_status

    # Mock session and CodeTest
    mock_session = mocker.MagicMock()
    mock_result = mocker.MagicMock()
    mocker.patch("code_management.test_writer.setup_db", return_value=mock_session)
    mocker.patch("code_management.test_writer.select", return_value=mocker.MagicMock())
    mock_session.execute.return_value.scalar_one.return_value = mock_result
    mock_session.commit.return_value = None

    # Call the function
    update_test_status(test_id=123, status="pass")

    # Assertions
    mock_result.test_status = "pass"
    mock_session.commit.assert_called_once()
