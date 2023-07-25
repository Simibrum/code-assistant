"""
This script would handle writing code to your Python files, 
including adding new functions or refactoring existing ones.
"""
import llm.llm_interface as llm
from functions import logger
import utils


def add_function_to_file(file_path: str, task_description: str):
    """
    Generate a new function based on a task description and add it to a Python file.

    Args:
        file_path (str): The path to the Python file.
        task_description (str): The description of the task for the new function.
    """
    # Generate code using the LLM.
    function_code, imports = llm.generate_code(task_description, function_file=file_path)

    if not function_code:
        print("No code generated.")
        return
    logger.debug("Function code: %s", function_code)

    if imports:
        logger.info("Writing imports to file: %s", imports)
        utils.add_imports(file_path, imports)

    # Append the generated code to the end of the file.
    with open(file_path, "a", encoding="utf-8") as file:
        file.write("\n" + function_code + "\n")


def generate_function_docstring(file_path: str, function_name: str):
    """
    Generate a docstring for a function.

    Args:
        file_path (str): The path to the Python file.
        function_name (str): The name of the function.
    """
    # Get the code of the function.
    function_code = utils.get_function_code(file_path, function_name)
    if function_code is None:
        print("Function not found.")
        return
    logger.debug("Function code: %s", function_code)

    # Generate the docstring.
    docstring = llm.generate_function_docstring(function_code)
    logger.debug("Docstring: %s", docstring)

    # Add the docstring to the function.
    utils.add_docstring_to_function(file_path, function_name, docstring)
