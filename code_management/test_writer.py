"""Code for generating test functions."""
import subprocess
from sqlalchemy import select
from code_management.code_database import setup_db
from code_management.code_database import CodeTest


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
    result = subprocess.run(
        ["pytest", string_test_identifier], capture_output=True, text=True
    )
    test_passed = result.returncode == 0
    return result.stdout, test_passed
