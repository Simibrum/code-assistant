"""
This is the main script that uses all the other components to perform tasks. 
It would contain the main loop of the agent, where it determines the next task, 
performs the task, evaluates the result, and repeats.
"""
import os
import ast
import argparse
import black
import utils
from functions import logger
import llm.llm_interface as llm


def generate_tests():
    """
    Generate tests for the functions in the codebase.
    """
    # Get the paths of all the python files in the present directory.
    python_files = utils.get_python_files()

    # Iterate through the files
    for python_file in python_files:
        # Extract the functions from the file.
        functions = utils.extract_functions_from_file(python_file)

        # Write the test to a file.
        test_file_name = f"tests/test_{python_file.split('/')[-1]}"

        # If the test file exists, extract the function names from it.
        existing_test_functions = set()
        if os.path.exists(test_file_name):
            logger.info("Test file %s already exists.", test_file_name)
            existing_test_functions = set(
                name for name, _ in utils.extract_functions_from_file(test_file_name)
            )
            logger.info("Found %s existing test functions.", len(existing_test_functions))
            logger.debug("Existing test functions: %s", existing_test_functions)

        # Iterate through the functions.
        for function_name, function_code in functions:
            # Only generate and write the test if it doesn't already exist.
            if f"test_{function_name}" not in existing_test_functions:
                # Generate a test for the function.
                logger.info("Generating test for function %s", function_name)
                test_code, imports = llm.generate_test(
                    function_code, function_file=python_file
                )
                if test_code is None:
                    logger.info("Failed to generate test for function %s", function_name)
                    continue
                logger.debug("Test code: %s", test_code)
                logger.info("Writing imports to file: %s", imports)
                utils.add_imports(test_file_name, imports)
                logger.info("Writing test to file %s", test_file_name)
                with open(test_file_name, "a", encoding="utf-8") as file:
                    file.write("\n\n" + test_code + "\n\n")


def generate_module_docstrings():
    """
    Generate module docstrings for all Python files that don't have one.
    """
    # Get the Python files in the directory.
    python_files = utils.get_python_files(skip_tests=False)

    # Process each file.
    for file_path in python_files:
        # Parse the existing code.
        with open(file_path, "r", encoding="utf-8") as file:
            module = ast.parse(file.read())

        # Check if the module has a docstring.
        if ast.get_docstring(module) is not None:
            logger.info("Module %s already has a docstring.", file_path)
            continue  # Skip this file if it has a docstring.

        logger.info("Generating docstring for module %s", file_path)
        # Generate a docstring for the module.
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()
        # Skip if the file is empty.
        if not file_contents:
            continue
        docstring = llm.generate_module_docstring(file_contents)
        logger.debug("Generated docstring: %s", docstring)

        # Add the docstring to the module.
        docstring_node = ast.Expr(value=ast.Str(s=docstring))
        module.body.insert(0, docstring_node)

        # Unparse the modified AST back to code.
        new_code = ast.unparse(module)
        logger.debug("New code: %s", new_code)
        # Format code with black
        fmt_code = utils.format_code(new_code)
        logger.debug("Formatted code: %s", fmt_code)
        logger.info("Writing docstring to file %s", file_path)
        # Write the modified code back to the file.
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(fmt_code)


def format_modules():
    """
    Format all Python files in the current directory.
    """
    # Get the Python files in the directory.
    python_files = utils.get_python_files(skip_tests=False)

    # Process each file.
    for file_path in python_files:
        # Parse the existing code.
        logger.info("Formatting module %s", file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            original_code = file.read()
        try:
            # Format code with black
            fmt_code = utils.format_code(original_code)
            logger.debug("Formatted code: %s", fmt_code)
            logger.info("Writing formatted code to file %s", file_path)
            # Write the modified code back to the file.
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(fmt_code)
        except black.NothingChanged:
            logger.info("No changes to file %s", file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate_tests", action="store_true")
    parser.add_argument("--generate_module_docstrings", action="store_true")
    parser.add_argument("--format_modules", action="store_true")
    args = parser.parse_args()

    if args.generate_tests:
        generate_tests()

    if args.generate_module_docstrings:
        generate_module_docstrings()

    if args.format_modules:
        format_modules()
