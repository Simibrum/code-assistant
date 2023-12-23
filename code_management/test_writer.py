"""Code for generating test functions."""
import re
import shutil

import subprocess  # nosec
from sqlalchemy import select
from code_management.code_database import setup_db
from code_management.code_database import CodeTest
from functions import logger
import llm.llm_interface
import utils
from git_management.git_handler import GitHandler


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
    logger.info("Running test ID %s", test_id)
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.id == test_id)
    result = session.execute(stmt).scalar_one()
    output, passed = run_specific_test(result.identifier)
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
        # Run the test
        output, passed = run_specific_test(test.identifier)

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
    logger.info("Getting revised test for test ID %s", test_id)
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
    # Return the revised test code
    return revised_test_code, imports


def fetch_failing_tests():
    """
    Fetches all failing tests from the database.

    :return: List of failing tests.
    """
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.test_status == "fail")
    failing_tests = session.execute(stmt).scalars().all()
    return failing_tests


def write_revised_test_to_file(test_name, test_file_name, revised_test_code, imports):
    """
    Writes the revised test code to the test file.

    :param test_name: The name of the test function to replace.
    :param test_file_name: Path to the test file.
    :param revised_test_code: The revised test code to insert.
    :param imports: The imports to add to the test file.
    """
    logger.info("Writing revised test to file: %s", test_file_name)
    if imports:
        logger.info("Writing imports to file: %s", imports)
        utils.add_imports(test_file_name, imports)
    success = replace_test_in_file(test_file_name, test_name, revised_test_code)
    if not success:
        logger.error("Failed to write revised test to file: %s", test_file_name)


def update_test_in_db(test_id, new_test_code, passed):
    """
    Updates the test code and status in the database.

    :param test_id: The ID of the test to update.
    :param new_test_code: The new test code to insert.
    :param passed: Boolean indicating whether the test passed or failed.
    """
    logger.info("Updating test ID %s", test_id)
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.id == test_id)
    test = session.execute(stmt).scalar_one()
    test.test_string = new_test_code
    test.test_status = "pass" if passed else "fail"
    session.commit()


def any_tests_still_failing():
    """
    Checks whether any tests are still failing.

    :return: True if any tests are still failing, False otherwise.
    """
    session = setup_db()
    stmt = select(CodeTest).where(CodeTest.test_status == "fail")
    failing_tests = session.execute(stmt).scalars().all()
    return len(failing_tests) > 0


def revise_and_test_loop(max_attempts_per_test):
    """
    Iterates over failing tests, revises each, and tests until passing or max attempts reached.

    :param max_attempts_per_test: Maximum number of revision attempts for each failing test.
    """
    # Fetch failing tests
    failing_tests = fetch_failing_tests()

    # If failing tests create a new temporary branch for test revisions
    if not failing_tests:
        logger.info("No failing tests found.")
        return
    git_handler = GitHandler()
    git_handler.create_temp_test_branch()

    for test in failing_tests:
        logger.info(f"Test {test.test_name} is failing, re-coding...")
        # Reset attempts and success flag
        attempts = 0
        success = False

        while attempts < max_attempts_per_test and not success:
            # Apply test revision logic
            revised_test_code, revised_imports = get_revised_test(test.id)

            # Write revised test to file
            write_revised_test_to_file(
                test.test_name, test.file_path, revised_test_code, revised_imports
            )

            # Run revised test
            output, passed = run_test_by_id(test.id)

            if passed:
                success = True
                logger.info(
                    f"Test {test.identifier} passed after {attempts + 1} attempts."
                )
            else:
                attempts += 1
                logger.info(
                    f"Test {test.identifier} failed on attempt {attempts}. Retrying..."
                )

            # Update test status in the database
            update_test_in_db(
                test.id, revised_test_code, passed
            )  # Placeholder function

        if not success:
            print(
                f"Test {test.identifier} failed after {max_attempts_per_test} attempts."
            )

        # Commit changes to Git for each test
        # Create a commit message that refers to the test name and number of attempts
        commit_message = f"Revised test {test.identifier} after {attempts} attempts."
        git_handler.commit_changes(commit_message)  # Placeholder function

    # Check for any remaining failing tests
    if any_tests_still_failing():
        logger.info("Some tests are still failing.")
        # Handle as needed (e.g., revert changes, log for manual review, etc.)
    else:
        logger.info("All tests passed or reached max attempts.")
        # Merge the temporary branch into the original branch
        git_handler.merge_temp_test_branch()
