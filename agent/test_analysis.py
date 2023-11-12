"""
    Functions to analyse test results and improve the code.
"""
import logging

import utils
from functions import logger


def parse_node_id(node_id: str) -> tuple[tuple[str, str]]:
    """
    Parse a node ID into a file path and a function name.

    Args:
        node_id (str): The node ID to parse.

    Returns:
        tuple[tuple[str, str]]: The file path and function name for the
        original function and the test function.
    """
    # Split the string at the "::" separator.
    file_path, function_name = node_id.split("::")

    # Split the file path at the "/" separator and take the last element.
    test_filename = file_path.split("/")[-1]
    original_filename = test_filename.split("test_", 1)[-1]

    # Split the function name at the "test_" and take the second element.
    original_function_name = function_name.split("test_", 1)[-1]

    return (
        (original_filename, original_function_name),
        (test_filename, function_name),
    )


def get_full_path(filename: str) -> str:
    """
    Get the full path to a file.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The full path to the file.
    """
    python_files = utils.get_python_files()
    for python_file in python_files:
        if python_file.endswith(filename):
            return python_file
    return ""


def run_tests_and_analyze_failures():
    """
    Runs pytest, captures the output of failed tests, identifies the failing test and the function
    being tested, retrieves the code for both, and sends that information to an LLM for analysis.
    """
    # Run pytest and load test output from JSON

    result = utils.run_pytest()
    logging.shutdown()

    # result has two main items "collectors" and "tests"
    # If collectors has results but tests is empty, collecting tests failed
    if result.get("collectors") and not result.get("tests"):
        logger.error("Collecting tests failed.")
        for node in result.get("collectors"):
            if node.get("outcome") == "failed":
                logger.error("Collector failed.")
                logger.error(node.get("nodeid"))
                logger.error(node.get("longrepr"))
            return

    if result.get("collectors") and result.get("tests"):
        logger.info("Collecting tests succeeded.")
        if any(node.get("outcome") == "failed" for node in result.get("tests")):
            logger.error("Some tests failed.")
        else:
            logger.info("All tests passed.")
            return
        for node in result.get("tests"):
            if node.get("outcome") == "failed":
                original_details, test_details = parse_node_id(node.get("nodeid"))
                filename, function_name = original_details
                full_path = get_full_path(filename)
                if not full_path:
                    logger.error("Could not find file %s", filename)
                    continue
                logger.info(
                    "Retrieving code for function %s in file %s",
                    function_name,
                    full_path,
                )
                function_code = utils.get_function_code(full_path, function_name)
                test_filename, test_function_name = test_details
                test_full_path = get_full_path(test_filename)
                logger.info(
                    "Retrieving code for function %s in file %s",
                    function_name,
                    full_path,
                )
                test_function_code = utils.get_function_code(
                    test_full_path, test_function_name
                )
                logger.debug("Function code: %s", function_code)
                logger.debug("Test function code: %s", test_function_code)
                logger.error("Test failed.")
                logger.error(node.get("nodeid"))
                # Look to see which of setup, call, or teardown failed
                if node.get("setup"):
                    setup_outcome = node.get("setup").get("outcome")
                    if setup_outcome == "failed":
                        logger.error("Setup failed.")
                        logger.error(node.get("setup"))
                if node.get("call"):
                    call_outcome = node.get("call").get("outcome")
                    if call_outcome == "failed":
                        logger.error("Call failed.")
                        logger.error(node.get("call"))
                if node.get("teardown"):
                    teardown_outcome = node.get("teardown").get("outcome")
                    if teardown_outcome == "failed":
                        logger.error("Teardown failed.")
                        logger.error(node.get("teardown"))
    return
