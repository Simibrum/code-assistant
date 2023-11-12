from agent import test_analysis


def test_parse_node_id():
    from agent.test_analysis import parse_node_id

    node_id = "./agent/test_analysis.py::test_parse_node_id"
    expected_output = (
        ("analysis.py", "parse_node_id"),
        ("test_analysis.py", "test_parse_node_id"),
    )
    assert parse_node_id(node_id) == expected_output
    node_id = "./agent/analysis.py::parse_node_id"
    expected_output = (
        ("analysis.py", "parse_node_id"),
        ("analysis.py", "parse_node_id"),
    )
    assert parse_node_id(node_id) == expected_output


def test_get_full_path():
    """
    Test the get_full_path function.
    """
    filename = "test_analysis.py"
    expected_path = "./agent/test_analysis.py"
    result = test_analysis.get_full_path(filename)
    assert result == expected_path


def test_run_tests_and_analyze_failures(mocker):
    """
    Tests the function run_tests_and_analyze_failures from the test_analysis module.
    The function is expected to run pytest, capture the output of failed tests, identify
    the failing test and the function being tested, retrieve the code for both, and
    send that information to an LLM for analysis.
    """
    # Mocking the utils.run_pytest function to return a specific result
    mocker.patch("utils.run_pytest", return_value={"collectors": [], "tests": []})

    # Mocking the logging.shutdown function as it does not need to be tested
    mocker.patch("logging.shutdown")

    # Importing the function to test
    from agent.test_analysis import run_tests_and_analyze_failures

    # Calling the function
    run_tests_and_analyze_failures()

    # There are no asserts in this test as the function does not return anything.
    # The test is for the function to run without any exceptions.
