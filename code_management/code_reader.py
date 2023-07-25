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

def read_function_descriptions(file_path: str) -> dict[str: str]:
    """
    Read the descriptions of the functions in a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        dict[str: str]: A dictionary of function name
         and function descriptions.
    """
    function_descriptions = dict()
    for function_name, function_code in utils.extract_functions_from_file(file_path):
        function_descriptions[function_name] = utils.read_function_description(function_code)
    return function_descriptions
