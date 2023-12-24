import json
import subprocess  # nosec B603, B404
from typing import Dict, Any

from code_management.code_database import setup_db, CodeClass, CodeFunction
from config import PROJECT_DIRECTORY
from functions import logger
import llm.llm_interface
from code_management.test_writer import write_revised_test_to_file


COVERAGE_JSON_PATH = f"{PROJECT_DIRECTORY}/coverage.json"


def run_pytest_coverage():
    """Run pytest with coverage and generate JSON report."""
    logger.info("Running pytest with coverage...")
    # Run pytest with coverage
    pytest_command = ["coverage", "run", "-m", "pytest"]
    subprocess.run(pytest_command, check=True)  # nosec B603
    logger.info("Generating JSON coverage report...")
    # Generate JSON coverage report
    coverage_json_command = ["coverage", "json"]
    subprocess.run(coverage_json_command, check=True)  # nosec B603


def parse_coverage_json(file_path: str) -> Dict[str, Any]:
    """
    Parses a coverage JSON file into a dictionary.

    Args:
        file_path (str): The path to the coverage JSON file.

    Returns:
        Dict[str, Any]: A dictionary containing the coverage data.
    """
    logger.info("Parsing coverage JSON file...")
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


# Assuming `parse_coverage_json` is already defined


def has_untested_lines(file_coverage, start_line, end_line):
    """Check if the line range has any untested lines."""
    missing_lines = file_coverage.get("missing", [])
    return any(
        line for line in range(start_line, end_line + 1) if line in missing_lines
    )


def check_code_coverage(coverage_data, code_objects):
    """Check coverage for a list of code objects (classes or functions)."""
    for obj in code_objects:
        file_coverage = coverage_data.get(obj.file_path, {})
        if has_untested_lines(file_coverage, obj.start_line, obj.end_line):
            obj.test_status = "Untested"
        else:
            obj.test_status = "Tested"
    return code_objects


def update_code_coverage(coverage_data, code_objects, session):
    """Check coverage for a list of code objects (classes or functions)."""
    logger.info("Updating code coverage in the database...")
    for obj in code_objects:
        # Remove "./" from file path
        file_path = (
            obj.file_path[2:] if obj.file_path.startswith("./") else obj.file_path
        )
        logger.info("Checking coverage for %s", file_path)
        file_coverage = coverage_data.get(file_path, {})
        logger.info("Coverage data for %s: %s", obj.name, file_coverage)
        missing_lines = file_coverage.get("missing_lines", [])
        logger.info("Missing lines for %s: %s", obj.name, missing_lines)
        obj.missing_lines.clear()
        for line in missing_lines:
            if obj.start_line <= line <= obj.end_line:
                logger.info("Adding missing line %s to %s", line, obj.name)
                obj.add_missing_line(line)
                session.add(obj)
                session.commit()
    session.commit()


def run_coverage_and_update_db():
    """Run coverage and update the database."""
    # Get the database session
    db_session = setup_db()
    # Get the code objects from the database
    code_objects = (
        db_session.query(CodeClass).all() + db_session.query(CodeFunction).all()
    )
    # Run pytest with coverage
    run_pytest_coverage()
    # Get the coverage data
    coverage_data = parse_coverage_json(COVERAGE_JSON_PATH)
    # Get the "files" portion of the coverage data
    coverage_data = coverage_data.get("files", {})
    # Check coverage
    checked_objects = check_code_coverage(coverage_data, code_objects)
    # Update the database
    update_code_coverage(coverage_data, checked_objects, db_session)
    # Close the database session
    db_session.close()


def get_objects_needing_extra_testing(db_session):
    """Get the code objects that need extra tests."""
    code_objects = db_session.query(CodeFunction).all()
    return [obj for obj in code_objects if obj.needs_extra_testing]


def revise_tests_to_increase_coverage():
    """Revise tests to increase coverage."""
    # Get the database session
    db_session = setup_db()
    # Get the code objects that need extra testing
    code_objects = get_objects_needing_extra_testing(db_session)
    # Iterate over the code objects
    for obj in code_objects:
        # Get original test
        original_test_obj = obj.tests[0] if obj.tests else None
        if not original_test_obj:
            # Generate a new test using existing logic
            continue
        else:
            # Get the original test code
            original_test_code = original_test_obj.code_string
            # Use the LLM to generate a new test
            (
                revised_test_code,
                imports,
            ) = llm.llm_interface.cover_missing_lines_with_tests(
                original_test_code=original_test_code,
                function_code=obj.code_string,
                start_line=obj.start_line,
                end_line=obj.end_line,
                missing_lines=obj.get_missing_lines(),
            )
            # Write the amended test to file
            write_revised_test_to_file(
                test_name=original_test_obj.name,
                test_file_name=original_test_obj.file_path,
                revised_test_code=revised_test_code,
                imports=imports,
            )
            # Update the database
            original_test_obj.code_string = revised_test_code
            original_test_obj.imports = imports
            db_session.add(original_test_obj)
            db_session.commit()
            # TODO - common code here with the iterative test writer?
    # TODO - we need to run the tests after the loop and fix any failing
    # tests, we then need to re-run the coverage checker and update the
    # database again
