"""
Module to read information from the code files.
"""
import utils

def read_code_file_descriptions(start_dir: str) -> dict:
    """
    Read the descriptions of the code files in a directory.

    Args:
        start_dir (str): The path to the directory to read.

    Returns:
        dict: A dictionary mapping file paths to file descriptions.
    """
    code_file_descriptions = {}
    for file_path in utils.get_python_files(start_dir):
        code_file_descriptions[file_path] = utils.read_file_description(file_path)
    return code_file_descriptions

def read_function_descriptions(file_path: str) -> list[str]:
    """
    Read the descriptions of the functions in a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list[str]: A list of function descriptions.
    """
    function_descriptions = []
    for function in utils.get_functions(file_path):
        function_descriptions.append(utils.read_function_description(function))
    return function_descriptions