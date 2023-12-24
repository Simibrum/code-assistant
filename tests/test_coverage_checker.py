import os
from code_management.coverage_checker import (
    parse_coverage_json,
    has_untested_lines,
    check_code_coverage,
    update_code_coverage,
)
from code_management.code_database import CodeClass, CodeFunction
from unittest.mock import MagicMock


def test_parse_coverage_json():
    """Test the parse_coverage_json function."""
    # Get the path to the current directory
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Replace this with the path to your test JSON file
    test_json_path = os.path.join(current_directory, "test_coverage.json")
    data = parse_coverage_json(test_json_path)

    assert isinstance(data, dict)
    # Add more assertions here based on expected structure of your JSON data


def test_has_untested_lines():
    # Mock coverage data
    file_coverage = {"missing": [2, 3, 5]}

    # Test ranges
    assert (
        has_untested_lines(file_coverage, 1, 4) is True
    )  # Range includes missing lines
    assert (
        has_untested_lines(file_coverage, 6, 10) is False
    )  # Range does not include missing lines


def test_check_code_coverage():
    # Mock coverage data
    coverage_data = {"some_file.py": {"missing": [2, 3, 5]}}

    # Mock code objects
    mock_class = CodeClass(
        start_line=1, end_line=4, file_path="some_file.py", test_status=None
    )
    mock_function = CodeFunction(
        start_line=6, end_line=10, file_path="some_file.py", test_status=None
    )

    # Check coverage
    checked_objects = check_code_coverage(coverage_data, [mock_class, mock_function])

    # Assert test_status is updated correctly
    assert checked_objects[0].test_status == "Untested"  # Class has untested lines
    assert (
        checked_objects[1].test_status == "Tested"
    )  # Function does not have untested lines


def test_update_code_coverage():
    class MockCodeObject:
        missing_lines = []
        name = "test_function"
        file_path = "test_file"
        start_line = 2
        end_line = 4

        def add_missing_line(self, line):
            self.missing_lines.append(line)

    # Define test data
    coverage_data = {"test_file": {"missing_lines": [1, 2, 3, 4, 5]}}

    code_objects = [MockCodeObject()]

    session = MagicMock()

    # Call the function under test
    update_code_coverage(coverage_data, code_objects, session)

    # Check that commit() was called
    session.commit.assert_called()

    # Check that the missing_lines property of the test object now includes the 2nd, 3rd and 4th lines
    assert code_objects[0].missing_lines == [2, 3, 4]
