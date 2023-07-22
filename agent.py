"""
This is the main script that uses all the other components to perform tasks. 
It would contain the main loop of the agent, where it determines the next task, 
performs the task, evaluates the result, and repeats.
"""
import os
import utils
import llm.llm_interface as llm


def generate_tests():
    """
    Generate tests for the functions in the codebase.
    """
    # Get the paths of all the python files in the present directory.
    python_files = [
        file for file in os.listdir() if file.endswith(".py") and utils.should_use_file(file)]

    # Iterate through the files
    for python_file in python_files:
        # Extract the functions from the file.
        functions = utils.extract_functions_from_file(python_file)

        # Write the test to a file.
        test_file_name = f"tests/test_{python_file}"
        
        # If the test file exists, extract the function names from it.
        existing_test_functions = set()
        if os.path.exists(test_file_name):
            existing_test_functions = set(
                name for name, _ in utils.extract_functions_from_file(test_file_name))

        # Iterate through the functions.
        for function_name, function_code in functions:
            # Only generate and write the test if it doesn't already exist.
            if function_name not in existing_test_functions:
                # Generate a test for the function.
                test_code = llm.generate_test(function_code)
                with open(test_file_name, "a", encoding="utf-8") as file:
                    file.write(test_code + "\n")

