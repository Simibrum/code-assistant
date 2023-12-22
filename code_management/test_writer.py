"""Code for generating test functions."""
import re
import shutil

import subprocess  # nosec
from sqlalchemy import select
from code_management.code_database import setup_db
from code_management.code_database import CodeTest
from functions import logger
import llm.llm_interface


def get_test_code(test_id):
    """Get the code for a test from the database."""
    session = setup_db()
    stmt = select(CodeTest).where(
        CodeTest.id == test_id
    )  # Assuming each test has an ID
    result = session.execute(stmt).scalar_one()
    return result.test_string


def get_function_code(test_id):
    """Get the code for the function being tested from the database."""
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.id == test_id)
    result = session.execute(stmt).scalar_one()
    return result.tested_function


def update_test_status(test_id, status):
    """Update the status of a test in the database."""
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.id == test_id)
    test = session.execute(stmt).scalar_one()
    test.test_status = status
    session.commit()


def run_specific_test(string_test_identifier):
    """
    Runs a specific pytest test, returns the stdout as a string, and indicates pass/fail.
    :param string_test_identifier: String identifier of the test (e.g., 'test_module.py::test_function')
    :return: Tuple containing stdout from the test run as a string and a boolean indicating pass (True) or fail (False)
    """
    pytest_path = shutil.which("pytest")
    if pytest_path is None:
        return "pytest is not installed.", False

    result = subprocess.run(
        [pytest_path, string_test_identifier], capture_output=True, text=True
    )  # nosec B603
    test_passed = result.returncode == 0
    return result.stdout, test_passed


def run_test_by_id(test_id: int):
    """Run a test by its ID."""
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.id == test_id)
    result = session.execute(stmt).scalar_one()
    test_identifier = f"{result.file_path}::{result.test_name}"
    output, passed = run_specific_test(test_identifier)
    return output, passed


def run_pre_commit_hooks():
    """
    Runs pre-commit hooks and returns the output as a string.
    :return: Output from the pre-commit hooks as a string.
    """
    pre_commit_path = shutil.which("pre-commit")
    if pre_commit_path is None:
        return "pre-commit is not installed."

    try:
        # Running the pre-commit command
        result = subprocess.run(
            [pre_commit_path, "run", "--all-files"], capture_output=True, text=True
        )  # nosec B603
        # Returning the stdout and stderr combined
        return result.stdout + result.stderr
    except FileNotFoundError:
        # Handling the case where pre-commit is not installed
        return "pre-commit is not installed."


def run_all_tests_and_update_status():
    """
    Iterates over all tests, runs each test, and updates the test_status based on the result.
    """
    session = setup_db()
    # Fetch all test records
    stmt = select(CodeTest)
    all_tests = session.execute(stmt).scalars().all()

    for test in all_tests:
        test_identifier = f"{test.file_path}::{test.test_name}"
        # Run the test
        output, passed = run_specific_test(test_identifier)

        # Update the test_status
        test_status = "pass" if passed else "fail"
        test.test_status = test_status
        session.commit()

        # Optionally, you can log or print the output and status
        logger.debug(f"Test ID {test.id}: {test_status}\nOutput: {output}")


def replace_test_in_file(test_file_name, old_test_name, new_test_code):
    """
    Replaces an existing test in a file with new test code.

    :param test_file_name: Path to the test file.
    :param old_test_name: The name of the test function to replace.
    :param new_test_code: The new test code to insert.
    :return: True if replacement is successful, False otherwise.
    """
    try:
        with open(test_file_name, "r", encoding="utf-8") as file:
            content = file.read()

        # Define a regular expression pattern to find the old test function
        # Assumes standard Python test function definitions
        pattern = rf"def {old_test_name}\(.*?\):.*?^(def |\Z)"
        if re.search(pattern, content, flags=re.DOTALL | re.MULTILINE):
            # Replace the old test function with new test code
            new_content = re.sub(
                pattern, f"{new_test_code}", content, flags=re.DOTALL | re.MULTILINE
            )

            with open(test_file_name, "w", encoding="utf-8") as file:
                file.write(new_content)
            return True
        else:
            print(f"Test function {old_test_name} not found in {test_file_name}.")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def get_revised_test(test_id: int):
    """Get the code for a test from the database."""
    # Get the test code
    test_code = get_test_code(test_id)
    # Get the function code
    function_code = get_function_code(test_id)
    # Get the failing test output
    output, passed = run_test_by_id(test_id)
    # Send to the LLM for revised code
    revised_test_code, imports = llm.llm_interface.revise_test(
        test_code, function_code, output
    )
